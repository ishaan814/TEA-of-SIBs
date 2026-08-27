# A Techno-Economic Analysis of Sodium-ion Batteries for Stationary Energy Storage

Bottom-up, pack-level techno-economic model comparing NVPF/hard carbon sodium-ion
cells against an LFP/graphite benchmark for stationary storage. Built as an
eight-module pipeline in Python and deployed as a Streamlit application.

MSc Design Engineering, Dyson School of Design Engineering, Imperial College London.
Supervisor: Dr Billy Wu.

The model follows the methodology of BatPaC v5.2 (Argonne National Laboratory),
re-implemented so that sodium-ion chemistry parameters can be varied and so that
material intensity, embodied carbon, levelised cost of storage and end-of-life
recovery can be added, none of which BatPaC contains.

---

## What is in this repository

| File | What it is |
|---|---|
| `app.py` | The model. This is the file you run. |
| `sib_studies.json` | The seven saved studies (S1-S7) plus the NMC811-G validation case. Needed to reproduce the results. |
| `check_batpac.py` | Utility that reads the BatPaC v5.2 workbook directly with `openpyxl`, used to extract parameter values the published manual does not state. |
| `TEA v1` … `v9` | Development history. Superseded snapshots kept for transparency; not needed to run anything. |

---

## Running the model

You need Python 3.11 or later.

```bash
pip install streamlit numpy pandas plotly openpyxl
streamlit run app.py
```

The interface opens in your browser at `http://localhost:8501`.

---

## Reproducing the results

Click **Load** in the top bar and pick a study from `sib_studies.json`. Loading
restores every input and the stored outputs of Modules 01 to 05.

Then work through the modules in order:

1. **Module 01 - Electrochemical Design.** Electrode area, layer count and the
   chemistry parameters go in.
2. **Module 02 - Cell Design.** Cell geometry, foil areas, electrolyte volume.
3. **Module 03 - Pack Design.** Module and pack topology, conductor sizing, pack mass.
4. **Module 04 - Manufacturing Cost.** Pack cost, built from 27 process steps.
5. **Module 05 - Sustainability and LCOS.** Material intensity, embodied carbon,
   levelised cost of storage, end-of-life recovery.

Modules 06 to 08 re-run the 01-04 chain under varied inputs and can be run in any
order once 01-05 have been run:

- **Module 06 - Sensitivity and Chemistry Comparison.** Tornado chart, the
  four-chemistry comparison, and the cost bridge.
- **Module 07 - Monte Carlo.** 10,000 iterations sampling all uncertain inputs together.
- **Module 08 - Parameter Sweeps.** Fourteen single-variable sweeps.

**Important:** changing any input in Modules 01 to 03 invalidates everything
downstream. Re-run the chain from that module onward. **Save** writes the current
state back to `sib_studies.json`.

---

## The studies

| Study | What it is |
|---|---|
| S1 | Laboratory baseline, 50 Ah cell |
| S2 | Same formulation, enlarged to 100 Ah |
| S3 | **Manufacturing-scale reference case.** The headline result. |
| S4 | Residential pack (10 kWh) built from the S3 cell |
| S5 | Commercial pack (111 kWh) built from the S3 cell |
| S6 | Utility pack (237 kWh) built from the S3 cell |
| S7 | LFP/graphite benchmark at S3 geometry and topology |
| NMC811-G | Validation case against the BatPaC v5.2 reference |

S1 to S3 hold the pack topology fixed and vary the cell. S4 to S6 hold the S3 cell
fixed and vary the pack. S7 changes only the electrochemistry, material prices,
current-collector metal, carbon intensities and cycle life, so the comparison
against S3 isolates chemistry from geometry.

---

## Where each result comes from

| Result | How to reproduce |
|---|---|
| Validation table | Load **NMC811-G**, read Modules 01 to 04 |
| Study results table | Load **S1** to **S6** in turn |
| Cost bridge | Load **S3**, run the cost bridge in Module 06 |
| Parameter sweeps | Load **S3**, run Module 08 |
| Tornado chart | Load **S3**, run the tornado in Module 06 |
| Monte Carlo distribution | Load **S3**, run Module 07 at 10,000 iterations, seed 42 |
| Chemistry comparison and parity surface | Load **S3**, run the chemistry comparison in Module 06 |
| Material intensity and embodied carbon | Load **S3** and **S7**, read Module 05 |

---

## Notes and limitations

- The model is **bottom-up**: electrode area and integer layer count are inputs and
  pack energy is the output. BatPaC works the other way round, taking target pack
  energy and deriving a layer count that it rounds. The direction is reversed here
  so that two chemistries can be compared on an identical physical cell.
- BatPaC's area-specific impedance and power model is not implemented. Conductors
  and terminals are sized on a nominal 0.5C discharge current instead, which suits
  stationary duty but means **rate capability cannot be assessed**.
- Embodied carbon covers **materials only**, at cell and pack level. Manufacturing
  energy, transport, use and disposal are excluded, so the figures are lower than a
  full cradle-to-gate assessment would give. The same boundary applies to both
  chemistries.
- Costs are for BatPaC's default US plant (labour $35/hr, energy $0.04/kWh, plant
  utilisation 100%). Absolute values are therefore US costs; the gap between
  chemistries is unaffected since both carry the same rates.
- Sodium-ion outputs are **projections, not observations**. No commercial NVPF plant
  exists to validate them against. Passing the NMC811-G validation shows the cost
  method is implemented correctly, not that the sodium-ion parameter set is right.

Every input, its source and its basis (measured, BatPaC default, derived or
estimated) is documented in the appendices of the accompanying thesis.
