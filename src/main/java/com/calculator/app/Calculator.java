package com.calculator.app;

/**
 * A comprehensive calculator class that provides various mathematical operations.
 * This class includes basic arithmetic operations as well as more advanced
 * mathematical functions like square root, power calculation, and percentage calculation.
 */
public class Calculator {
    
    /**
     * Adds two numbers together.
     *
     * @param a first number (addend)
     * @param b second number (addend)
     * @return the sum of a and b
     */
    public double add(double a, double b) {
        return a + b;
    }
    
    /**
     * Subtracts the second number from the first.
     *
     * @param a first number (minuend)
     * @param b second number (subtrahend)
     * @return the difference of a and b (a - b)
     */
    public double subtract(double a, double b) {
        return a - b;
    }
    
    /**
     * Multiplies two numbers together.
     *
     * @param a first number (multiplicand)
     * @param b second number (multiplier)
     * @return the product of a and b
     */
    public double multiply(double a, double b) {
        return a * b;
    }
    
    /**
     * Divides the first number by the second.
     *
     * @param a first number (dividend)
     * @param b second number (divisor)
     * @return the quotient of a divided by b (a / b)
     * @throws ArithmeticException if b is zero, as division by zero is undefined
     */
    public double divide(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return a / b;
    }
    
    /**
     * Calculates the square root of a number.
     *
     * @param number the non-negative number to calculate the square root of
     * @return the square root of the input number
     * @throws IllegalArgumentException if the input number is negative, as square root of negative numbers is not defined in real number system
     */
    public double calculateSquareRoot(double number) {
        if (number < 0) {
            throw new IllegalArgumentException("Cannot calculate square root of a negative number");
        }
        return Math.sqrt(number);
    }
    
    /**
     * Calculates the power of a base number raised to an exponent.
     *
     * @param base the base number
     * @param exponent the exponent to raise the base to
     * @return the result of base raised to the power of exponent (base^exponent)
     * @note Special cases:
     *       - If the exponent is 0, the result is 1.0 (any number raised to 0 is 1)
     *       - If the base is 0 and exponent is positive, the result is 0.0
     *       - If the base is negative and exponent is fractional, the result may be NaN
     */
    public double calculatePower(double base, double exponent) {
        return Math.pow(base, exponent);
    }
    
    /**
     * Calculates the percentage of a given value.
     *
     * @param value the base value to calculate percentage of
     * @param percentage the percentage to calculate (e.g., 20 for 20%)
     * @return the calculated percentage of the value (value * percentage / 100)
     * @example calculatePercentage(200, 10) returns 20.0 (10% of 200)
     */
    public double calculatePercentage(double value, double percentage) {
        return (value * percentage) / 100.0;
    }
    
    /**
     * Calculates the absolute value of a number.
     *
     * @param number the input number
     * @return the absolute (non-negative) value of the input number
     * @example calculateAbsoluteValue(-5.5) returns 5.5
     */
    public double calculateAbsoluteValue(double number) {
        return Math.abs(number);
    }
    
    /**
     * Rounds a decimal number to the specified number of decimal places.
     *
     * @param number the number to round
     * @param decimalPlaces the number of decimal places to round to (must be non-negative)
     * @return the rounded number
     * @throws IllegalArgumentException if decimalPlaces is negative
     * @example roundToDecimalPlaces(3.14159, 2) returns 3.14
     */
    public double roundToDecimalPlaces(double number, int decimalPlaces) {
        if (decimalPlaces < 0) {
            throw new IllegalArgumentException("Decimal places must be non-negative");
        }
        double factor = Math.pow(10, decimalPlaces);
        return Math.round(number * factor) / factor;
    }
}

// Made with Bob
