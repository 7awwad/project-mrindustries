1. What approach did you take for garment overlay and why?
I took a Landmark-Anchored 2D Matrix Transformation approach.

Pose Detection: I used MediaPipe to extract human pose landmarks, specifically isolating the shoulders (Points 11 & 12) and hips (Points 23 & 24).

Isolation: I used rembg to remove the background of both the person and the garment.

Scaling & Anchoring: I calculated the Euclidean distance between the shoulder landmarks to determine the user's physical width. The garment is then dynamically resized using a specific multiplier (1.6x for tops) to account for 3D body volume on a 2D plane. Finally, I used foolproof alpha-blending with bounds-checking to overlay the garment.

2. What were the biggest challenges you faced?
The most significant challenge was "invisible pixel padding" left over from garment background removal. Initially, when the engine scaled the garment to fit the shoulders, the actual visible fabric was tiny because the code was scaling the massive invisible bounding box around it.

The Solution: I implemented an advanced contour mapping system (cv2.findContours) to threshold the alpha channel, strip away the invisible ghost padding, and draw a tight bounding box around the actual physical fabric.

Secondary Challenge: Distinguishing between tops and trousers. I solved this by calculating the garment's aspect ratio (height vs. width) to dynamically shift the anchor points to either the shoulders or the waist/hips.

3. What does not work well in your current solution?
Because this is a 2D affine transformation pipeline, it lacks cloth physics and depth.

The garment does not warp around the physical curves of the user's body (like wrapping around the ribcage).

It does not account for user pose depths (e.g., if the user is slightly turned sideways, the shirt remains perfectly flat).

Lighting and shadows between the user's room and the garment's studio lighting are mismatched, breaking the illusion of realism.

4. If you had 2 weeks instead of 72 hours, what would you build differently?
Warping Matrix: I would implement Thin Plate Spline (TPS) warping. By mapping grid points on the garment to the dense mesh of the human body, the clothes would stretch and fold naturally.

Database & Auth: I would replace the current hardcoded Streamlit session state with a proper backend (Node.js/Express or FastAPI) and a PostgreSQL database.

Advanced Recommender: I would upgrade the content-based recommender to a hybrid model utilizing collaborative filtering (Matrix Factorization).

5. What production-grade models would you use for real deployment?
DCI-VTON / VITON-HD: These models are specifically trained for high-resolution, image-based virtual try-on and naturally handle fabric drape and body occlusions.

Stable Diffusion (Inpainting + ControlNet): Using ControlNet (specifically DensePose or OpenPose models) alongside Stable Diffusion would allow us to generate the garment onto the user while perfectly matching the lighting and shadows.

Segment Anything Model (SAM) by Meta: For flawless, zero-shot background removal and garment extraction.

🚀 How to Run the Project
Follow these steps to set up and run the Aura Vision platform on your local machine:

1. Prerequisites
Ensure you have Python 3.9 or higher installed on your system.

2. Clone the Repository
Open your terminal or command prompt and clone this repository:

Bash
git clone <your-github-repo-link>
cd <your-repo-name>
3. Set Up a Virtual Environment (Recommended)
It is best practice to run the app in a virtual environment to avoid library conflicts:

Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
4. Install Dependencies
Install all required libraries using the requirements.txt file:

Bash
pip install -r requirements.txt
Note: The first time you run the app, it may take a moment to download the U2-Net model for background removal.

5. Launch the Application
Run the Streamlit server:

Bash
streamlit run app.py
6. Usage Instructions
Lookbook: Browse the curated collection by selecting a community from the sidebar.

Virtual Try-On: Click "✦ VIRTUAL TRY-ON" on any product to enter the fitting suite.

Processing: Upload your photo and a garment photo, then click "PROCESS AI FITTING".

Results: View your estimated body measurements and download the final overlayed image.