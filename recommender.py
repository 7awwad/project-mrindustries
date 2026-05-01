import pandas as pd
import numpy as np
import os

class AuraRecommender:
    def __init__(self):
        self.csv_path = "products.csv"
        if not os.path.exists(self.csv_path):
            self._generate_dataset()
        self.df = pd.read_csv(self.csv_path)

    def _generate_dataset(self):
        """
        TASK 3: Creates a rich dataset of 60 products with community,
        category, price, rating, and detailed tags for content-based filtering.
        """
        products = {
            "Muslim": [
                ("Embroidered Abaya - Ramadan Edit",       "Full Body",  2499, 4.8, "abaya, embroidery, ramadan, modest, black, formal"),
                ("Printed Hijab - Floral Eid",             "Accessory",   699, 4.6, "hijab, floral, eid, modest, colorful, lightweight"),
                ("Premium Kurta - Jumuah Special",         "Top",        1899, 4.7, "kurta, jumuah, formal, premium, white, islamic"),
                ("Palazzo Set - Modest Chic",              "Bottom",     1499, 4.5, "palazzo, modest, casual, loose, comfortable"),
                ("Kaftan Dress - Eid Collection",          "Full Body",  3499, 4.9, "kaftan, eid, luxury, festive, gold, embellished"),
                ("Tasbeeh Bracelet - Prayer Edition",      "Accessory",   399, 4.4, "tasbeeh, prayer, accessory, spiritual, beads"),
                ("Niqab - Premium Chiffon",                "Accessory",   599, 4.3, "niqab, modest, chiffon, daily, breathable"),
                ("Shalwar Kameez - Classic White",         "Full Body",  2199, 4.7, "shalwar, kameez, classic, formal, eid, white"),
                ("Men's Thobe - Luxury Linen",             "Full Body",  3299, 4.8, "thobe, men, linen, luxury, formal, friday"),
                ("Modest Swimwear - Burkini",              "Full Body",  2799, 4.5, "burkini, modest, swim, beach, sport, full-cover"),
                ("Embroidered Khussa - Festive",           "Accessory",   999, 4.6, "khussa, shoes, festive, embroidered, ethnic"),
                ("Lace Abaya - Bridal Edition",            "Full Body",  5499, 4.9, "abaya, lace, bridal, premium, wedding, white"),
            ],
            "Hindu": [
                ("Banarasi Silk Saree - Diwali Special",  "Full Body",  4999, 4.9, "saree, banarasi, silk, diwali, festive, wedding"),
                ("Anarkali Suit - Navratri Edition",      "Full Body",  3299, 4.7, "anarkali, navratri, festive, embroidered, ethnic"),
                ("Puja Dhoti - Panchagajam",              "Bottom",      999, 4.5, "dhoti, puja, ritual, cotton, traditional, white"),
                ("Lehenga Choli - Bridal Red",            "Full Body",  7999, 4.9, "lehenga, bridal, red, wedding, embellished, heavy"),
                ("Kundan Necklace Set - Temple Jewelry",  "Accessory",  2499, 4.8, "kundan, necklace, temple, jewelry, gold, festive"),
                ("Men's Kurta Pajama - Diwali Gold",      "Full Body",  2199, 4.7, "kurta, pajama, men, diwali, gold, silk"),
                ("Chanderi Cotton Kurta - Daily Wear",    "Top",         899, 4.4, "kurta, chanderi, cotton, daily, casual, printed"),
                ("Maang Tikka - Bridal Set",              "Accessory",  1299, 4.6, "maang tikka, bridal, gold, head jewelry, wedding"),
                ("Patola Silk Dupatta - Gujarat Heritage","Accessory",  1799, 4.5, "dupatta, patola, silk, gujarat, heritage, colorful"),
                ("Dhoti Kurta - Pongal Edition",          "Full Body",  1999, 4.6, "dhoti, kurta, pongal, south indian, traditional"),
                ("Kasavu Saree - Kerala Onam",            "Full Body",  3499, 4.8, "saree, kasavu, kerala, onam, gold border, cotton"),
                ("Sharara Set - Festive Pink",            "Full Body",  2799, 4.7, "sharara, festive, pink, embroidered, party"),
            ],
            "Sikh": [
                ("Phulkari Dupatta - Vaisakhi Heritage",  "Accessory",  1499, 4.7, "phulkari, embroidery, vaisakhi, punjabi, colorful"),
                ("Patiala Salwar - Classic Mustard",      "Full Body",  1799, 4.6, "patiala, salwar, kameez, punjabi, mustard, classic"),
                ("Groom's Sherwani - Anand Karaj",        "Full Body",  6999, 4.9, "sherwani, groom, wedding, anand karaj, cream, zari"),
                ("Turban Fabric - Gurmukhi Blue",         "Accessory",   899, 4.5, "turban, dastar, sikh, blue, fabric, religious"),
                ("Bridal Lehenga - Gurpurab Red",         "Full Body",  7499, 4.8, "lehenga, bridal, red, gurpurab, embroidered, heavy"),
                ("Kara Kada - Stainless Steel",           "Accessory",   599, 4.7, "kara, kada, sikh, steel, religious, daily"),
                ("Kurta Pajama - Lohri Mustard",          "Full Body",  2299, 4.5, "kurta, pajama, lohri, mustard, festive, men"),
                ("Punjabi Jutti - Embroidered Gold",      "Accessory",  1199, 4.6, "jutti, shoes, punjabi, gold, embroidered, ethnic"),
                ("Salwar Kameez - Gidda Edition",         "Full Body",  2699, 4.7, "salwar, kameez, gidda, dance, colorful, folk"),
                ("Silk Dupatta - Baisakhi Gold",          "Accessory",   999, 4.4, "dupatta, silk, baisakhi, gold, festive"),
                ("Men's Waistcoat - Harvest Edition",     "Top",        1599, 4.5, "waistcoat, men, harvest, lohri, embroidered"),
                ("Churidar Set - Amritsar Heritage",      "Full Body",  2199, 4.6, "churidar, amritsar, heritage, embroidery, blue"),
            ],
            "Christian": [
                ("Floral Midi Dress - Easter Sunday",     "Full Body",  2799, 4.7, "midi, dress, easter, floral, modest, spring"),
                ("Men's Blazer - Sunday Service",         "Top",        3499, 4.8, "blazer, men, church, formal, sunday, classic"),
                ("Pearl Necklace - First Communion",      "Accessory",  1299, 4.6, "pearl, necklace, communion, formal, white, classic"),
                ("A-Line Dress - Christmas Crimson",      "Full Body",  2499, 4.5, "a-line, dress, christmas, red, formal, festive"),
                ("Lace Veil - Bridal Grace",              "Accessory",  1999, 4.8, "veil, lace, bridal, wedding, white, cathedral"),
                ("Choir Robe - Praise Edition",           "Full Body",  1799, 4.4, "robe, choir, church, formal, white, praise"),
                ("Men's Suit - Confirmation Navy",        "Full Body",  4999, 4.9, "suit, men, confirmation, navy, formal, classic"),
                ("Cross Pendant - Sterling Silver",       "Accessory",   799, 4.7, "cross, pendant, silver, religious, daily, faith"),
                ("Chiffon Blouse - Sunday Brunch",        "Top",        1499, 4.5, "blouse, chiffon, church, casual, modest, sunday"),
                ("Flared Skirt - Easter Pastels",         "Bottom",     1199, 4.4, "skirt, flared, easter, pastels, spring, modest"),
                ("Cardigan Set - Harvest Festival",       "Top",        2199, 4.6, "cardigan, harvest, festival, cozy, modest, fall"),
                ("Bridesmaid Gown - Chapel Sage",         "Full Body",  3999, 4.8, "gown, bridesmaid, wedding, sage, formal, elegant"),
            ],
            "Buddhist": [
                ("Linen Meditation Robe - Saffron",       "Full Body",  2299, 4.8, "robe, saffron, meditation, buddhist, zen, linen"),
                ("Cotton Kurta - Mindful White",          "Top",         899, 4.6, "kurta, cotton, white, minimal, meditation, calm"),
                ("Mala Bracelet - Bodhi Seed",            "Accessory",   499, 4.7, "mala, bracelet, bodhi, seed, meditation, prayer"),
                ("Linen Wide-Leg Pants - Zen Garden",     "Bottom",     1199, 4.5, "pants, linen, wide-leg, zen, relaxed, breathable"),
                ("Embroidered Shawl - Himalayan Blue",    "Accessory",  1699, 4.8, "shawl, embroidered, himalayan, blue, meditation, wrap"),
                ("Silk Kimono Top - Temple Edition",      "Top",        2499, 4.7, "kimono, silk, temple, japanese, elegant, calm"),
                ("Handloom Dhoti - Dharma White",         "Bottom",      799, 4.4, "dhoti, handloom, white, dharma, simple, pure"),
                ("Prayer Flag Scarf - Tibetan Symbols",   "Accessory",   999, 4.6, "scarf, prayer flag, tibetan, colorful, spiritual"),
                ("Hemp Meditation Hoodie - Earth",        "Top",        1899, 4.5, "hoodie, hemp, meditation, earth, sustainable, cozy"),
                ("Linen Set - Vesak Full Moon",           "Full Body",  2099, 4.7, "linen, set, vesak, full moon, white, peaceful"),
                ("Thangka Printed Tote - Dharma Art",    "Accessory",   699, 4.3, "tote, thangka, art, dharma, printed, daily"),
                ("Breathable Yoga Kurta - Pali Cotton",   "Top",        1299, 4.6, "kurta, yoga, pali, cotton, breathable, flexible"),
            ],
        }

        rows = []
        pid = 1001
        for comm, items in products.items():
            for (name, cat, price, rating, tags) in items:
                rows.append({
                    "product_id": pid,
                    "name": name,
                    "community": comm,
                    "category": cat,
                    "price": price,
                    "rating": rating,
                    "tags": tags,
                })
                pid += 1

        pd.DataFrame(rows).to_csv(self.csv_path, index=False)
        print(f"[Aura] Dataset generated: {len(rows)} products saved to {self.csv_path}")

    # ─────────────────────────────────────────────────────────────────────
    # TASK 3: Content-Based Recommendation Engine
    # ─────────────────────────────────────────────────────────────────────
    def get_recommendations(self, user_profile: dict, top_n: int = 10) -> list[dict]:
        """
        Full Task 3 recommendation pipeline.

        user_profile example:
        {
            "community": "Muslim",
            "preferred_categories": ["Full Body", "Accessory"],
            "price_range": (500, 3000),
            "past_purchases": ["abaya", "hijab", "eid"]
        }

        Returns list of dicts with product info + 'explanation' key.
        """
        self.df = pd.read_csv(self.csv_path)
        df = self.df.copy()

        # Step 1 — Filter by community
        community = user_profile.get("community", "")
        df = df[df["community"].str.lower() == community.lower()]

        # Step 2 — Filter by price range
        lo, hi = user_profile.get("price_range", (0, 999999))
        df = df[(df["price"] >= lo) & (df["price"] <= hi)]

        if df.empty:
            return []

        # Step 3 — Content-based scoring
        preferred_cats  = [c.lower() for c in user_profile.get("preferred_categories", [])]
        past_tags       = [t.lower().strip() for t in user_profile.get("past_purchases", [])]

        def relevance_score(row):
            score = 0.0
            tags = [t.strip().lower() for t in row["tags"].split(",")]

            # Category match
            if row["category"].lower() in preferred_cats:
                score += 2.0

            # Tag overlap with past purchases
            overlap = len(set(tags) & set(past_tags))
            score += overlap * 1.5

            return score

        df = df.copy()
        df["relevance"] = df.apply(relevance_score, axis=1)

        # Step 4 — Composite ranking: 60% rating + 40% relevance (normalised)
        max_rel = df["relevance"].max() or 1
        df["final_score"] = (df["rating"] / 5.0) * 0.6 + (df["relevance"] / max_rel) * 0.4
        df = df.sort_values("final_score", ascending=False).head(top_n)

        # Step 5 — Build output with explanation
        results = []
        for _, row in df.iterrows():
            tags = [t.strip() for t in row["tags"].split(",")]
            matched = list(set(tags) & set(past_tags))

            if matched:
                reason = f"Matches your interest in {', '.join(matched[:2])}."
            elif row["category"].lower() in preferred_cats:
                reason = f"In your preferred category: {row['category']}."
            else:
                reason = f"Top-rated {row['category'].lower()} in your community."

            results.append({
                **row.to_dict(),
                "explanation": reason,
            })
        return results

    # ─────────────────────────────────────────────────────────────────────
    # Lookbook helper (used by app.py for the catalog grid)
    # ─────────────────────────────────────────────────────────────────────
    def get_curated_collection(self, community_name: str, max_items: int = 6) -> list[dict]:
        """Returns top-rated items for a community — used by the Lookbook view."""
        self.df = pd.read_csv(self.csv_path)
        filtered = self.df[self.df["community"].str.lower() == community_name.lower()]
        return filtered.sort_values("rating", ascending=False).head(max_items).to_dict(orient="records")