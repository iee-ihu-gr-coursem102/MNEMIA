import os
import httpx
from fastapi import FastAPI, HTTPException, Query
from dotenv import load_dotenv

# Φόρτωση μεταβλητών περιβάλλοντος από το τοπικό αρχείο .env
load_dotenv()

app = FastAPI(title="Mnemia API")

# Ασφαλής ανάκτηση του API Key από το περιβάλλον συστήματος
EUROPEANA_API_KEY = os.getenv("EUROPEANA_API_KEY")

@app.get("/api/search/")
async def search_europeana(q: str = Query(..., description="Η λέξη-κλειδί για την αναζήτηση αντικειμένων")):
    """
    Δέχεται το query του χρήστη, επικοινωνεί με το Europeana API,
    φιλτράρει το παραγόμενο JSON και επιστρέφει τα καθαρά αποτελέσματα στο Frontend.
    """
    if not EUROPEANA_API_KEY:
        raise HTTPException(status_code=500, detail="Κρίσιμο Σφάλμα: Το Europeana API Key δεν έχει ρυθμιστεί στο αρχείο .env.")

    # Ορισμός του απομακρυσμένου URL και των παραμέτρων του αιτήματος HTTP GET
    url = "https://api.europeana.eu/record/v2/search.json"
    params = {
        "wskey": EUROPEANA_API_KEY,
        "query": q,
        "rows": 12  # Καθορισμός του πλήθους των επιστρεφόμενων αντικειμένων
    }

    try:
        # Ασύγχρονη εκτέλεση του HTTP request
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            
        # Έλεγχος ακεραιότητας της απόκρισης
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Σφάλμα API Europeana: {response.text}")
            
        data = response.json()
        raw_items = data.get("items", [])
        
        # Διαδικασία φιλτραρίσματος και εξαγωγής των απαιτούμενων πεδίων
        clean_results = []
        for item in raw_items:
            # Το API επιστρέφει συχνά τα δεδομένα ως λίστες (arrays). 
            # Χρησιμοποιούμε τη μέθοδο get και λαμβάνουμε το στοιχείο [0] με ασφάλεια (Index safety).
            filtered_item = {
                "id": item.get("id", ""),
                "title": item.get("title", ["Μη διαθέσιμος τίτλος"])[0] if item.get("title") else "Μη διαθέσιμος τίτλος",
                "creator": item.get("dcCreator", ["Άγνωστος δημιουργός"])[0] if item.get("dcCreator") else "Άγνωστος δημιουργός",
                "image_url": item.get("edmPreview", [""])[0] if item.get("edmPreview") else None,
                "date": item.get("year", ["Μη διαθέσιμη χρονολογία"])[0] if item.get("year") else "Μη διαθέσιμη χρονολογία"
            }
            clean_results.append(filtered_item)

        # Επιστροφή της καθαρής δομής δεδομένων (JSON)
        return {"results": clean_results}

    except httpx.RequestError as e:
        # Διαχείριση σφαλμάτων δικτύου
        raise HTTPException(status_code=503, detail=f"Αποτυχία σύνδεσης στο Europeana API: {str(e)}")