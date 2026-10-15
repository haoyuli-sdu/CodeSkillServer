---
name: "porting-code"
description: "Use to port code to another programming language"
---

# Porting code

This skill is used for porting code from one language to another language.

## Input

- Target language
- Source files or code to port

## Process

Start by creating an outline of key functionality that is present in the current code. Note any:

- Edge cases that the code or unit tests account for
- Libraries used and recommended equivalents in the target language.

Use the structured user input or question tool to walk through each library used and verify with the user which equivalent to use.

Additional options to present:

- Stub library functionality
- Implement from scratch

Next port any unit tests. Use this as a basis for verifying the ported code.

Finally port the code using the outline prepared earlier. Iterate on this using the unit tests to inform fixes.

## General guidelines

- Use patterns that are common for the target language.
- Use naming conventions that are common for the target language.
- The ported code should mirror the original code so that its easy for the user to find equivalent functionality.
- Maintain logging and comments that are present in original code.
- Note any new edge cases.
- Note any changes to the structure of the code to help the user orient themselves.

## Success criteria

- [ ] Unit tests pass, if present.
- [ ] Linting passes, if present.
- [ ] All key pieces of functionality are implemented.
- [ ] All identified edge cases are accounted for.
- [ ] All needed libraries are installed and ready to use.

## Examples

### Example original code

```ts
/**
 * Calculate the final price of the product including any discounts and with tax.
 * 
 * Throws an error on an invalid discount. 
 */
export function calculatePrice(basePrice: number, discount: number | null, taxRate: number): number {
	let discountAmount = 0;

	if (discount) {
		if (discount >= 1) {
			// If the discounts are misconfigured they can end up calculating a
			// negative price. Halt before showing the user an invalid price.
			throw new Error('Invalid discount');
		}

		discountAmount = basePrice * discount;
	}

	const taxAmount = (basePrice - discountAmount) * taxRate;

	return (basePrice - discountAmount) + taxAmount;
}
```

### Example outline

Key functionality:

- The `calculatePrice` function accepts a base price, discount percent, and a tax rate and calculates the final price of the product.
	- Edge cases:
		- Discount can be null
		- If discount is greater than or equal to 1, throw an exception to prevent invalid prices.

### Example ported code

```py
def calculate_price(base_price: float, discount: Optional[float], tax_rate: float) -> float:
	"""
	Calculate the final price of the product including any discounts and with tax.

	Raises an exception on an invalid discount.
	"""
	discount_amount = 0

	if discount is not None:
		if discount >= 1:
			# If the discounts are misconfigured they can end up calculating a
			# negative price. Halt before showing the user an invalid price.
			raise Exception('Invalid discount')

		discount_amount = base_price * discount

	tax_amount = (base_price - discount_amount) * tax_rate

	return (base_price - discount_amount) + tax_amount
```

### Example response

I ported the code to Python.

- `calculatePrice` is now `calculate_price`

