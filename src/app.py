"""Webapp Flask per la gestione dei rimborsi spese dei dipendenti."""

from flask import Flask, redirect, render_template, request, url_for

from src import calculator, rules, storage, validator

app = Flask(__name__)


def _numero(valore):
    try:
        return float(valore)
    except (TypeError, ValueError):
        return None


def _intero(valore):
    try:
        return int(valore)
    except (TypeError, ValueError):
        return None


def _registra(form):
    """Valida, calcola e registra una nuova richiesta. Restituisce la richiesta salvata."""
    richieste = storage.carica()
    categoria = form.get("categoria") or ""
    richiesta = {
        "id": storage.prossimo_id(richieste),
        "dipendente": (form.get("dipendente") or "").strip(),
        "data": form.get("data") or "",
        "categoria": categoria,
        "importo": _numero(form.get("importo")),
        "giorni": _intero(form.get("giorni")) if categoria in rules.CATEGORIE_A_GIORNATE else None,
        "km": _numero(form.get("km")) if categoria == "chilometrico" else None,
        "notti": _intero(form.get("notti")) if categoria == "alloggio" else None,
    }
    ok, motivazione = validator.valida(richiesta)
    if ok:
        ok, motivazione = validator.controlla_incompatibilita(richiesta, richieste)
    if ok:
        mese_rif = storage.mese(richiesta)
        dipendente = richiesta["dipendente"]
        gia_riconosciuta = storage.esente_riconosciuta_nel_mese(richieste, dipendente, mese_rif)
        giorni_agile = storage.giorni_agile_nel_mese(richieste, dipendente, mese_rif)
        esente, imponibile, dettaglio = calculator.calcola(richiesta, gia_riconosciuta, giorni_agile)
        richiesta.update(
            stato="valida",
            motivazione="",
            quota_esente=esente,
            quota_imponibile=imponibile,
            dettaglio=dettaglio,
        )
    else:
        richiesta.update(
            stato="respinta",
            motivazione=motivazione,
            quota_esente=0.0,
            quota_imponibile=0.0,
            dettaglio=None,
        )
    richieste.append(richiesta)
    storage.salva(richieste)
    return richiesta


@app.get("/")
def home():
    return redirect(url_for("elenco"))


@app.route("/nuova", methods=["GET", "POST"])
def nuova_richiesta():
    esito = None
    if request.method == "POST":
        esito = _registra(request.form)
    return render_template("nuova_richiesta.html", categorie=rules.CATEGORIE, esito=esito, rules=rules)


@app.get("/richieste")
def elenco():
    richieste = storage.carica()
    dipendente = request.args.get("dipendente", "")
    mese = request.args.get("mese", "")
    filtrate = [
        r
        for r in richieste
        if (not dipendente or r["dipendente"] == dipendente)
        and (not mese or storage.mese(r) == mese)
    ]
    filtrate.sort(key=lambda r: (r["data"], r["id"]), reverse=True)
    return render_template(
        "elenco.html",
        richieste=filtrate,
        categorie=rules.CATEGORIE,
        dipendenti=sorted({r["dipendente"] for r in richieste}),
        mesi=sorted({storage.mese(r) for r in richieste}, reverse=True),
        filtro_dipendente=dipendente,
        filtro_mese=mese,
    )


@app.get("/riepilogo")
def riepilogo():
    richieste = storage.carica()
    gruppi = {}
    for r in richieste:
        if r["stato"] != "valida":
            continue
        chiave = (storage.mese(r), r["dipendente"])
        gruppo = gruppi.setdefault(
            chiave, {"esente": 0.0, "imponibile": 0.0, "richieste": 0}
        )
        gruppo["esente"] = round(gruppo["esente"] + r["quota_esente"], 2)
        gruppo["imponibile"] = round(gruppo["imponibile"] + r["quota_imponibile"], 2)
        gruppo["richieste"] += 1
    righe = [
        {
            "mese": mese,
            "dipendente": dipendente,
            "esente": dati["esente"],
            "imponibile": dati["imponibile"],
            "richieste": dati["richieste"],
            "percentuale_plafond": min(
                round(
                    dati["esente"]
                    / (rules.PLAFOND_MENSILE if mese >= "2026-01" else rules.PLAFOND_MENSILE_2025)
                    * 100
                ),
                100,
            ),
        }
        for (mese, dipendente), dati in sorted(gruppi.items(), reverse=True)
    ]
    return render_template(
        "riepilogo.html",
        righe=righe,
        plafond=rules.PLAFOND_MENSILE,
        plafond_2025=rules.PLAFOND_MENSILE_2025,
    )


@app.get("/normativa")
def normativa():
    return render_template("normativa.html", rules=rules)


if __name__ == "__main__":
    import os
    app.run(debug=os.environ.get("FLASK_DEBUG", "0") == "1")
