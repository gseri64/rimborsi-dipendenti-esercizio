from src import calculator


def richiesta(**campi):
    base = {
        "dipendente": "Maria Rossi",
        "data": "2025-10-06",
        "categoria": "pasto",
        "importo": 10.0,
        "giorni": 1,
        "km": None,
        "notti": None,
    }
    base.update(campi)
    return base


class TestMassimaleTeorico:
    def test_trasferta_italia(self):
        r = richiesta(categoria="trasferta_italia", giorni=4)
        assert calculator.massimale_teorico(r) == 185.92

    def test_trasferta_estero(self):
        r = richiesta(categoria="trasferta_estero", giorni=3)
        assert calculator.massimale_teorico(r) == 232.41

    def test_pasto(self):
        r = richiesta(categoria="pasto", giorni=5)
        assert calculator.massimale_teorico(r) == 40.0

    def test_chilometrico(self):
        r = richiesta(categoria="chilometrico", km=250)
        assert calculator.massimale_teorico(r) == 105.0

    def test_alloggio(self):
        r = richiesta(categoria="alloggio", notti=2)
        assert calculator.massimale_teorico(r) == 300.0


class TestCalcola:
    def test_importo_sotto_massimale_tutto_esente(self):
        r = richiesta(categoria="pasto", giorni=5, importo=35.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 35.0
        assert imponibile == 0.0

    def test_importo_sopra_massimale_eccedenza_imponibile(self):
        r = richiesta(categoria="trasferta_italia", giorni=2, importo=120.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert esente == 92.96
        assert imponibile == 27.04

    def test_plafond_incapiente_limita_la_quota_esente(self):
        r = richiesta(categoria="alloggio", notti=2, importo=300.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert esente == 100.0
        assert imponibile == 200.0

    def test_plafond_esaurito_tutto_imponibile(self):
        r = richiesta(categoria="pasto", giorni=1, importo=8.0)
        esente, imponibile, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0
        assert imponibile == 8.0

    def test_dettaglio_del_calcolo(self):
        r = richiesta(categoria="trasferta_estero", giorni=2, importo=200.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=1100.0)
        assert dettaglio["massimale_teorico"] == 154.94
        assert dettaglio["esente_teorica"] == 154.94
        assert dettaglio["capienza_plafond"] == 100.0
        assert dettaglio["esente_effettiva"] == 100.0  # cappata dal plafond

    def test_dettaglio_esente_effettiva_uguale_teorica_senza_cap(self):
        r = richiesta(categoria="pasto", giorni=3, importo=20.0)
        _, _, dettaglio = calculator.calcola(r, esente_gia_riconosciuta=0.0)
        assert dettaglio["esente_teorica"] == dettaglio["esente_effettiva"]


class TestMassimaleEstero2026:
    def test_5_giorni_solo_fascia_piena(self):
        r = richiesta(categoria="trasferta_estero", data="2026-01-10", giorni=5)
        assert calculator.massimale_teorico(r) == 5 * 85.00  # 425.00

    def test_6_giorni_prima_riduzione(self):
        r = richiesta(categoria="trasferta_estero", data="2026-01-10", giorni=6)
        assert calculator.massimale_teorico(r) == 5 * 85.00 + 1 * 76.50  # 501.50

    def test_10_giorni_boundary_seconda_fascia(self):
        r = richiesta(categoria="trasferta_estero", data="2026-01-10", giorni=10)
        assert calculator.massimale_teorico(r) == 5 * 85.00 + 5 * 76.50  # 807.50

    def test_11_giorni_seconda_riduzione(self):
        r = richiesta(categoria="trasferta_estero", data="2026-01-10", giorni=11)
        assert calculator.massimale_teorico(r) == 5 * 85.00 + 5 * 76.50 + 1 * 68.00  # 875.50

    def test_12_giorni(self):
        r = richiesta(categoria="trasferta_estero", data="2026-01-10", giorni=12)
        assert calculator.massimale_teorico(r) == 943.50

    def test_estero_2025_nessuna_riduzione_progressiva(self):
        r = richiesta(categoria="trasferta_estero", data="2025-12-31", giorni=12)
        assert calculator.massimale_teorico(r) == round(77.47 * 12, 2)  # 929.64


class TestLavoroAgile:
    def test_cap_mensile_pieno(self):
        r = richiesta(categoria="lavoro_agile", data="2026-01-10", giorni=6, importo=21.0)
        assert calculator.massimale_teorico(r, giorni_agile_gia_usati=0) == 6 * 3.50  # 21.00

    def test_cap_mensile_residuo_parziale(self):
        r = richiesta(categoria="lavoro_agile", data="2026-01-10", giorni=6, importo=21.0)
        assert calculator.massimale_teorico(r, giorni_agile_gia_usati=8) == 4 * 3.50  # 14.00

    def test_cap_mensile_esaurito_massimale_zero(self):
        r = richiesta(categoria="lavoro_agile", data="2026-01-10", giorni=1, importo=3.50)
        assert calculator.massimale_teorico(r, giorni_agile_gia_usati=12) == 0.00

    def test_tutto_imponibile_se_cap_esaurito(self):
        r = richiesta(categoria="lavoro_agile", data="2026-01-10", giorni=3, importo=10.50)
        esente, imponibile, _ = calculator.calcola(r, 0.0, giorni_agile_gia_usati=12)
        assert esente == 0.00
        assert imponibile == 10.50


class TestRegimeTransitorio:
    def test_pasto_31_dicembre_2025_vecchio_massimale(self):
        r = richiesta(categoria="pasto", data="2025-12-31", giorni=1, importo=10.0)
        assert calculator.massimale_teorico(r) == 8.00

    def test_pasto_1_gennaio_2026_nuovo_massimale(self):
        r = richiesta(categoria="pasto", data="2026-01-01", giorni=1, importo=10.0)
        assert calculator.massimale_teorico(r) == 10.00

    def test_plafond_dicembre_2025_e_1200(self):
        r = richiesta(categoria="pasto", data="2025-12-20", giorni=1, importo=8.0)
        esente, _, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 0.0

    def test_plafond_gennaio_2026_e_1400(self):
        r = richiesta(categoria="pasto", data="2026-01-05", giorni=1, importo=10.0)
        esente, _, _ = calculator.calcola(r, esente_gia_riconosciuta=1200.0)
        assert esente == 10.0  # rimangono 200 € di capienza nel plafond 2026
