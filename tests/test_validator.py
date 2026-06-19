from src import validator


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


def test_richiesta_valida():
    assert validator.valida(richiesta()) == (True, "")


def test_dipendente_mancante():
    ok, motivazione = validator.valida(richiesta(dipendente=""))
    assert not ok
    assert motivazione == "dipendente mancante"


def test_categoria_non_riconosciuta():
    ok, motivazione = validator.valida(richiesta(categoria="parcheggio"))
    assert not ok
    assert motivazione == "categoria non riconosciuta"


def test_importo_zero():
    ok, motivazione = validator.valida(richiesta(importo=0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_negativo():
    ok, motivazione = validator.valida(richiesta(importo=-5.0))
    assert not ok
    assert motivazione == "importo non positivo"


def test_importo_mancante():
    ok, motivazione = validator.valida(richiesta(importo=None))
    assert not ok
    assert motivazione == "importo non positivo"


def test_data_mancante():
    ok, motivazione = validator.valida(richiesta(data=""))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_data_non_valida():
    ok, motivazione = validator.valida(richiesta(data="06/10/2025"))
    assert not ok
    assert motivazione == "data mancante o non valida"


def test_giornate_mancanti_per_trasferta():
    ok, motivazione = validator.valida(
        richiesta(categoria="trasferta_italia", giorni=None)
    )
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_giornate_zero_per_pasto():
    ok, motivazione = validator.valida(richiesta(categoria="pasto", giorni=0))
    assert not ok
    assert motivazione == "numero di giornate non valido"


def test_chilometri_non_validi():
    ok, motivazione = validator.valida(
        richiesta(categoria="chilometrico", km=0)
    )
    assert not ok
    assert motivazione == "numero di chilometri non valido"


def test_notti_non_valide():
    ok, motivazione = validator.valida(
        richiesta(categoria="alloggio", notti=None)
    )
    assert not ok
    assert motivazione == "numero di notti non valido"


def test_chilometrico_valido():
    assert validator.valida(
        richiesta(categoria="chilometrico", km=120, giorni=None)
    ) == (True, "")


def test_alloggio_valido():
    assert validator.valida(
        richiesta(categoria="alloggio", notti=3, giorni=None)
    ) == (True, "")


def test_lavoro_agile_ante_2026_respinto():
    ok, motivazione = validator.valida(
        richiesta(categoria="lavoro_agile", data="2025-12-31", giorni=1)
    )
    assert not ok
    assert "01/01/2026" in motivazione


def test_lavoro_agile_dal_2026_valido():
    assert validator.valida(
        richiesta(categoria="lavoro_agile", data="2026-01-01", giorni=1)
    ) == (True, "")


class TestIncompatibilita:
    def _trasferta(self, data="2026-03-02", giorni=5):
        return {
            "dipendente": "Mario", "categoria": "trasferta_italia",
            "data": data, "giorni": giorni, "stato": "valida",
        }

    def _agile(self, data, giorni=1):
        return {
            "dipendente": "Mario", "categoria": "lavoro_agile",
            "data": data, "giorni": giorni,
        }

    def test_agile_sovrapposto_a_trasferta_respinto(self):
        ok, msg = validator.controlla_incompatibilita(
            self._agile("2026-03-04"), [self._trasferta()]
        )
        assert not ok
        assert "incompatibilità" in msg

    def test_agile_adiacente_non_sovrapposto_ok(self):
        # trasferta 02-06 marzo (5 gg), agile dal 07
        ok, _ = validator.controlla_incompatibilita(
            self._agile("2026-03-07"), [self._trasferta()]
        )
        assert ok

    def test_trasferta_sovrapposta_ad_agile_respinta(self):
        esistente = {"dipendente": "Mario", "categoria": "lavoro_agile",
                     "data": "2026-03-10", "giorni": 2, "stato": "valida"}
        nuova = {"dipendente": "Mario", "categoria": "trasferta_estero",
                 "data": "2026-03-10", "giorni": 1}
        ok, _ = validator.controlla_incompatibilita(nuova, [esistente])
        assert not ok

    def test_richiesta_respinta_non_genera_incompatibilita(self):
        esistente = {**self._trasferta(), "stato": "respinta"}
        ok, _ = validator.controlla_incompatibilita(self._agile("2026-03-04"), [esistente])
        assert ok

    def test_incompatibilita_non_applicata_ante_2026(self):
        esistente = {"dipendente": "Mario", "categoria": "trasferta_italia",
                     "data": "2025-11-03", "giorni": 3, "stato": "valida"}
        nuova = {"dipendente": "Mario", "categoria": "lavoro_agile",
                 "data": "2025-11-04", "giorni": 1}
        ok, _ = validator.controlla_incompatibilita(nuova, [esistente])
        assert ok

    def test_giorni_none_su_richiesta_esistente_non_causa_crash(self):
        esistente = {"dipendente": "Mario", "categoria": "trasferta_italia",
                     "data": "2026-03-02", "giorni": None, "stato": "valida"}
        nuova = self._agile("2026-03-02")
        ok, _ = validator.controlla_incompatibilita(nuova, [esistente])
        assert ok  # giorni=None → set vuoto → nessun conflitto
