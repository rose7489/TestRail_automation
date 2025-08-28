package com.calculator.app;

/**
 * A simple calculator class that provides basic arithmetic operations.
 */
public class Calculator {
    
    /**
     * Adds two numbers.
     * 
     * @param a first number
     * @param b second number
     * @return the sum of a and b
     */
    public double add(double a, double b) {
        return a + b;
    }
    
    /**
     * Subtracts the second number from the first.
     * 
     * @param a first number
     * @param b second number
     * @return the result of a - b
     */
    public double subtract(double a, double b) {
        return a - b;
    }
    
    /**
     * Multiplies two numbers.
     * 
     * @param a first number
     * @param b second number
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
     * @return the result of a / b
     * @throws ArithmeticException if b is zero
     */
    public double divide(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("Division by zero is not allowed");
        }
        return a / b;
    }
}

// Made with Bob
