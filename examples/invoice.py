"""A small invoice that has to divide evenly across three cost centres.

Run from the repository root:  PYTHONPATH=src python examples/invoice.py
"""

from decimal import Decimal

from centwise import Money

line_items = [
    ("design", "480.00"),
    ("implementation", "1250.00"),
    ("review", "300.00"),
]
tax_rate = Decimal("0.0825")

subtotal = sum((Money(amount, "USD") for _, amount in line_items), Money.zero("USD"))
tax = subtotal * tax_rate
total = subtotal + tax

print(f"subtotal   {subtotal}")
print(f"tax 8.25%  {tax}")
print(f"total      {total}")

cost_centres = {"product": 2, "engineering": 5, "operations": 3}
shares = total.allocate(list(cost_centres.values()))
for (name, _), share in zip(cost_centres.items(), shares):
    print(f"{name:<12} {share}")

assert sum((share.amount for share in shares), Decimal(0)) == total.amount
print(f"shares sum {sum((share.amount for share in shares), Decimal(0))}")
