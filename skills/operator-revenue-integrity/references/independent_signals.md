# Independent signals — what each one can actually establish

Thresholds below are the ones the Aria Code realty agents apply
(`agents/realty/energy_anomaly.py`, `agents/realty/cashflow_verify.py`). They
are starting points calibrated for small commercial food-and-retail tenancies,
not universal constants — a business with a walk-in freezer or an EV charger
has a different baseline, and the benchmark should be reset per format before
any of these fire.

## Electricity / water consumption

**Establishes**: that the premises were in use, roughly in proportion to
activity. Meters are read by the utility, not the operator, which is what makes
them independent.

**Signals in use**:

| Condition | Reading |
|---|---|
| `elec < 10 kWh` + `revenue < 1000` + `entries < 5` | Likely vacant — not underreporting, a different problem |
| `energy_per_revenue > 3× benchmark` | Consumption far exceeds reported sales — possible off-book trade |
| `energy_per_revenue < 0.3× benchmark` and `elec > 50` | High consumption, low reported revenue — the classic underreporting shape |
| `night_electricity > 40% of total` | Activity outside declared operating hours |
| Consumption down >30% period-over-period | Business contracting — a commercial fact, not necessarily a reporting one |

**False alarms**: seasonal HVAC swings dominate the ratio in summer and winter;
a new appliance shifts the baseline permanently; shared or sub-metered premises
attribute another tenant's load to this one. Always confirm the meter serves
only this unit before treating a ratio as evidence.

## Door access, parking, foot traffic

**Establishes**: customer presence, independent of what was rung up.

**Signal in use**: revenue-per-visit far below benchmark (`< 0.3×`) means
customers came in and spent less than the format implies — either the sales
were not recorded, or the business genuinely changed.

**False alarms**: staff and delivery riders inflate entry counts; a counter
sited at a shared lobby door counts passers-by. Establish what the sensor
actually counts before dividing by it.

## Delivery / group-buy platform settlements

**Establishes**: revenue the platform paid out. This is the strongest
independent signal available, because the number originates with a third party
that has no incentive to help the operator understate it.

**Limitation**: covers only the delivery channel. A strong platform figure says
nothing about dine-in or walk-in cash.

## Inventory and purchase records

**Establishes**: implied revenue, by grossing purchase cost up through an
expected margin. `cashflow_verify` flags declared revenue below 60% of
inventory-implied revenue.

**False alarms**: stock-building before a promotion, spoilage and waste, and a
margin assumption that no longer matches the menu. The margin input is the
weak link — a wrong margin moves the implied figure more than most real
underreporting would.

## Bank settlement records

**Establishes**: money that actually moved through a visible account.

**Limitation**: only as independent as the account coverage. An operator with a
second, undisclosed receiving account produces bank records that are accurate
and incomplete simultaneously. `cashflow_verify` treats an unauthorized change
of receiving account as a high-severity finding for exactly this reason —
account changes are how the independent signal gets quietly severed.

## Cash ratio

**Establishes**: how much of the reported activity is inherently unverifiable.
A cash share above 30% is flagged not as evidence of wrongdoing but as a
measure of how little of the figure can be checked at all.

## Reading the combination

No single signal is conclusive. The shape that matters is **several
independent signals pointing the same direction at once** — high utility
consumption, healthy foot traffic, and strong delivery settlements alongside a
weak declared figure is a much stronger finding than any one of them. The
agents scale confidence with the number of independent sources actually
present, and the write-up should carry that same caveat: with one source, the
honest verdict is "unverified", not "clean".
