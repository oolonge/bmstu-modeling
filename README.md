# Modelling

BMSTU IU7, semester 7.

Simulation of stochastic systems: random number generation, Markov chains,
queueing systems modelled event by event, and the same systems rebuilt in GPSS
for comparison. Desktop interfaces in PyQt6.

## Structure

| Path                             | Topic                                           |
|----------------------------------|-------------------------------------------------|
| `lab-01-random-generators`       | Linear congruential generator, uniformity tests |
| `lab-02-markov-chains`           | Markov process, steady-state probabilities      |
| `lab-03-distributions`           | Distribution laws and their parameters          |
| `lab-04-queueing-system`         | Queueing system, event-driven simulation        |
| `lab-05-information-center`      | Information centre: three operators, two hosts  |
| `lab-06-information-center-gpss` | The same centre expressed in GPSS               |
| `lab-07-gpss-queue`              | GPSS: minimal queue size with no losses         |
| `lab-08-gpss-information-center` | GPSS: rejection probability of the centre       |
| `docs`                           | Lectures and title pages                        |

Labs 4-6 share a layout: `models/` for the simulation core, `gui/` for the
PyQt6 windows, `constants.py` for parameters, `report/` for the LaTeX report.

## Run

```sh
pip install numpy scipy matplotlib PyQt6
cd lab-05-information-center && python main.py
```

## Stack

Python, NumPy, SciPy, PyQt6, GPSS
