import cv2
import mediapipe as mp
import numpy as np
from rembg import remove

# ── TASK 4 (BONUS): Garment Classifier ───────────────────────────────────────
# We use CLIP via transformers for zero-shot classification — no fine-tuning needed.
# Falls back gracefully if torch / transformers are not installed.
try:
    from transformers import CLIPProcessor, CLIPModel
    from PIL import Image
    import torch
    import io

    _clip_model     = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    CLIP_AVAILABLE  = True
except Exception:
    CLIP_AVAILABLE  = False
# ─────────────────────────────────────────────────────────────────────────────


class VastraEngine:
    GARMENT_LABELS = ["Top", "Bottom", "Full Length", "Headwear", "Accessory"]

    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose    = self.mp_pose.Pose(
            static_image_mode=True,
            min_detection_confidence=0.5,
        )

    # ── Utility ──────────────────────────────────────────────────────────────
    def overlay_alpha(self, background, overlay, x, y):
        """Alpha-composite `overlay` (RGBA) onto `background` (BGR) at (x, y)."""
        h_bg, w_bg = background.shape[:2]
        h_ov, w_ov = overlay.shape[:2]

        y1, y2   = max(0, y),  min(h_bg, y + h_ov)
        x1, x2   = max(0, x),  min(w_bg, x + w_ov)
        y1o, y2o = max(0, -y), min(h_ov, h_bg - y)
        x1o, x2o = max(0, -x), min(w_ov, w_bg - x)

        if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
            return background

        img_crop     = background[y1:y2, x1:x2].astype(np.float32)
        overlay_crop = overlay[y1o:y2o, x1o:x2o]
        alpha        = overlay_crop[:, :, 3:4].astype(np.float32) / 255.0

        blended = alpha * overlay_crop[:, :, :3].astype(np.float32) + (1.0 - alpha) * img_crop
        background[y1:y2, x1:x2] = np.clip(blended, 0, 255).astype(np.uint8)
        return background

    # ── TASK 2: Body Measurement Estimation ──────────────────────────────────
    def estimate_measurements(self, results, height_cm: int) -> dict:
        """
        Converts MediaPipe normalised landmark coords → real-world cm estimates.
        Returns shoulder_width, torso_length, hip_width and a recommended size.
        """
        if not results or not results.pose_landmarks:
            return {"error": "Could not detect body landmarks. Ensure a clear, full-body photo."}

        lm = results.pose_landmarks.landmark

        # Reference: nose (0) to left ankle (27) spans the full body height in Y
        nose_y   = lm[0].y
        ankle_y  = (lm[27].y + lm[28].y) / 2          # average both ankles
        px_height = abs(nose_y - ankle_y) or 0.75       # fallback to 75 % of image

        cm_per_unit = height_cm / px_height

        # Shoulder width — left (11) to right (12) shoulder
        shoulder_w = abs(lm[11].x - lm[12].x) * cm_per_unit

        # Hip width — left (23) to right (24) hip
        hip_w = abs(lm[23].x - lm[24].x) * cm_per_unit

        # Torso length — mid-shoulder Y to mid-hip Y
        mid_sh_y  = (lm[11].y + lm[12].y) / 2
        mid_hip_y = (lm[23].y + lm[24].y) / 2
        torso_l   = abs(mid_sh_y - mid_hip_y) * cm_per_unit

        # Size recommendation based on shoulder width
        if shoulder_w < 38:
            size = "XS"
        elif shoulder_w < 43:
            size = "S"
        elif shoulder_w < 48:
            size = "M"
        elif shoulder_w < 53:
            size = "L"
        else:
            size = "XL"

        return {
            "shoulder_width":    f"{round(shoulder_w, 1)} cm",
            "torso_length":      f"{round(torso_l, 1)} cm",
            "hip_width":         f"{round(hip_w, 1)} cm",
            "recommended_size":  size,
        }

    # ── TASK 4 (BONUS): Garment Classifier ───────────────────────────────────
    def classify_garment(self, garment_bytes: bytes) -> dict:
        """
        TASK 4: Zero-shot garment classification using CLIP.
        Returns { "class": str, "confidence": float, "all_scores": dict }

        Falls back to a rule-based colour/shape heuristic if CLIP is unavailable.
        """
        if CLIP_AVAILABLE:
            try:
                pil_img = Image.open(io.BytesIO(garment_bytes)).convert("RGB")
                prompts = [f"a photo of a {lbl.lower()} garment" for lbl in self.GARMENT_LABELS]

                inputs  = _clip_processor(text=prompts, images=pil_img, return_tensors="pt", padding=True)
                with torch.no_grad():
                    logits = _clip_model(**inputs).logits_per_image[0]
                probs   = torch.softmax(logits, dim=0).numpy()

                best_idx   = int(np.argmax(probs))
                return {
                    "class":      self.GARMENT_LABELS[best_idx],
                    "confidence": round(float(probs[best_idx]) * 100, 1),
                    "all_scores": {
                        lbl: round(float(p) * 100, 1)
                        for lbl, p in zip(self.GARMENT_LABELS, probs)
                    },
                    "model": "CLIP (openai/clip-vit-base-patch32)",
                }
            except Exception as e:
                return {"class": "Unknown", "confidence": 0.0, "error": str(e)}
        else:
            # Lightweight heuristic fallback (aspect ratio + dominant-colour centroid)
            arr    = np.frombuffer(garment_bytes, np.uint8)
            img    = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if img is None:
                return {"class": "Unknown", "confidence": 0.0, "error": "Could not decode image."}

            h, w   = img.shape[:2]
            ratio  = h / max(w, 1)

            if ratio > 1.8:
                cls, conf = "Full Length", 72.0
            elif ratio > 1.2:
                cls, conf = "Top", 65.0
            elif ratio < 0.6:
                cls, conf = "Bottom", 60.0
            else:
                cls, conf = "Accessory", 55.0

            return {
                "class":      cls,
                "confidence": conf,
                "model":      "Heuristic (install transformers+torch for CLIP)",
            }

    # ── TASK 1: Virtual Try-On ────────────────────────────────────────────────
    def execute_tryon(self, person_bytes: bytes, garment_bytes: bytes, height_cm: int) -> tuple:
        """
        TASK 1 pipeline:
          1. Remove background from person → place on brand background (#F9F7F4)
          2. Remove background from garment
          3. Detect pose landmarks
          4. Scale + overlay garment aligned to shoulders/torso
          5. Return (PNG bytes, info_dict)

        info_dict contains:
          - measurements  (Task 2)
          - garment_class (Task 4 bonus)
        """
        info = {}

        # ── Step 1: Person background removal ────────────────────────────────
        person_original = cv2.imdecode(np.frombuffer(person_bytes, np.uint8), cv2.IMREAD_COLOR)
        if person_original is None:
            return None, {"error": "Could not decode person image."}

        h, w = person_original.shape[:2]

        person_no_bg_raw = remove(person_bytes)
        person_rgba      = cv2.imdecode(np.frombuffer(person_no_bg_raw, np.uint8), cv2.IMREAD_UNCHANGED)

        # Brand background: #F9F7F4 → BGR (244, 247, 249)
        canvas = np.full((h, w, 3), (244, 247, 249), dtype=np.uint8)
        alpha_p = person_rgba[:, :, 3:4].astype(np.float32) / 255.0
        canvas  = (alpha_p * person_rgba[:, :, :3] + (1.0 - alpha_p) * canvas).astype(np.uint8)

        # ── Step 2: Garment background removal ───────────────────────────────
        garment_raw  = remove(garment_bytes)
        garment_rgba = cv2.imdecode(np.frombuffer(garment_raw, np.uint8), cv2.IMREAD_UNCHANGED)

        # Tight crop via alpha contour
        alpha_ch    = garment_rgba[:, :, 3]
        _, thresh   = cv2.threshold(alpha_ch, 20, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            cx, cy, cw, ch = cv2.boundingRect(max(contours, key=cv2.contourArea))
            garment_rgba   = garment_rgba[cy:cy + ch, cx:cx + cw]

        # ── Step 3: Pose detection ────────────────────────────────────────────
        rgb_orig = cv2.cvtColor(person_original, cv2.COLOR_BGR2RGB)
        results  = self.pose.process(rgb_orig)

        if not results.pose_landmarks:
            return None, {"error": "Could not detect body pose. Use a clear, well-lit, full-body photo."}

        # ── Step 4: Measurements (Task 2) ────────────────────────────────────
        info["measurements"] = self.estimate_measurements(results, height_cm)

        # ── Step 5: Garment classification (Task 4 bonus) ────────────────────
        info["garment_class"] = self.classify_garment(garment_bytes)

        # ── Step 6: Scale & position garment ─────────────────────────────────
        lm    = results.pose_landmarks.landmark
        r_sh  = (int(lm[11].x * w), int(lm[11].y * h))
        l_sh  = (int(lm[12].x * w), int(lm[12].y * h))

        sh_dist  = np.linalg.norm(np.array(r_sh) - np.array(l_sh))
        target_w = int(sh_dist * 1.7)                          # slightly wider for a natural drape
        aspect   = garment_rgba.shape[0] / max(garment_rgba.shape[1], 1)
        target_h = int(target_w * aspect)

        garment_resized = cv2.resize(garment_rgba, (target_w, target_h), interpolation=cv2.INTER_LANCZOS4)

        mid_x    = (r_sh[0] + l_sh[0]) // 2
        mid_y    = (r_sh[1] + l_sh[1]) // 2
        offset_x = mid_x - target_w // 2
        offset_y = mid_y - int(target_h * 0.08)               # nudge garment up slightly

        # ── Step 7: Composite & encode ────────────────────────────────────────
        final = self.overlay_alpha(canvas, garment_resized, offset_x, offset_y)
        _, buf = cv2.imencode(".png", final)
        return buf.tobytes(), info