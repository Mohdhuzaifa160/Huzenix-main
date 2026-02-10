"""
Calculator module for Huzenix.
Handles mathematical calculations.
"""

import re


class Calculator:
    """Performs simple calculations."""

    @staticmethod
    def calculate(query: str) -> str:
        """
        Parse and evaluate a mathematical expression.

        Args:
            query: User query containing math expression

        Returns:
            Calculation result string
        """
        # Extract numbers and operators
        expression = Calculator._extract_expression(query)
        
        if not expression:
            return "I couldn't understand the calculation. Please try again."

        try:
            # Safe evaluation: only numbers, +, -, *, /, (, )
            if not all(c in "0123456789+-*/()." for c in expression.replace(" ", "")):
                return "Invalid mathematical expression."
            
            result = eval(expression)
            return f"The answer is {result}"
        except (ValueError, SyntaxError, ZeroDivisionError):
            return "I couldn't calculate that. Please check your expression."

    @staticmethod
    def _extract_expression(query: str) -> str:
        """Extract mathematical expression from query."""
        # Remove common prefixes
        query = query.replace("what is", "").replace("calculate", "").strip()
        
        # Find sequence of numbers and operators
        match = re.search(r"[\d\s+\-*/().]+", query)
        return match.group(0) if match else None
