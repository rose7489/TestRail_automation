package com.calculator.app;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for the Calculator class.
 * This class contains tests for all calculator operations to ensure they work correctly.
 */
public class CalculatorTest {
    
    private Calculator calculator;
    
    @BeforeEach
    public void setUp() {
        calculator = new Calculator();
    }
    
    @Test
    public void testAddition() {
        assertEquals(5.0, calculator.add(2.0, 3.0), 0.0001);
        assertEquals(0.0, calculator.add(0.0, 0.0), 0.0001);
        assertEquals(-1.0, calculator.add(2.0, -3.0), 0.0001);
        assertEquals(1.5, calculator.add(0.5, 1.0), 0.0001);
    }
    
    @Test
    public void testSubtraction() {
        assertEquals(-1.0, calculator.subtract(2.0, 3.0), 0.0001);
        assertEquals(0.0, calculator.subtract(0.0, 0.0), 0.0001);
        assertEquals(5.0, calculator.subtract(2.0, -3.0), 0.0001);
        assertEquals(-0.5, calculator.subtract(0.5, 1.0), 0.0001);
    }
    
    @Test
    public void testMultiplication() {
        assertEquals(6.0, calculator.multiply(2.0, 3.0), 0.0001);
        assertEquals(0.0, calculator.multiply(0.0, 5.0), 0.0001);
        assertEquals(-6.0, calculator.multiply(2.0, -3.0), 0.0001);
        assertEquals(0.5, calculator.multiply(0.5, 1.0), 0.0001);
    }
    
    @Test
    public void testDivision() {
        assertEquals(2.0, calculator.divide(6.0, 3.0), 0.0001);
        assertEquals(0.0, calculator.divide(0.0, 5.0), 0.0001);
        assertEquals(-2.0, calculator.divide(6.0, -3.0), 0.0001);
        assertEquals(0.5, calculator.divide(0.5, 1.0), 0.0001);
    }
    
    @Test
    public void testDivisionByZero() {
        Exception exception = assertThrows(ArithmeticException.class, () -> {
            calculator.divide(5.0, 0.0);
        });
        
        String expectedMessage = "Division by zero is not allowed";
        String actualMessage = exception.getMessage();
        
        assertTrue(actualMessage.contains(expectedMessage));
    }
    
    @Test
    public void testCalculateSquareRoot() {
        assertEquals(2.0, calculator.calculateSquareRoot(4.0), 0.0001);
        assertEquals(0.0, calculator.calculateSquareRoot(0.0), 0.0001);
        assertEquals(1.5, calculator.calculateSquareRoot(2.25), 0.0001);
        assertEquals(3.0, calculator.calculateSquareRoot(9.0), 0.0001);
    }
    
    @Test
    public void testCalculateSquareRootWithNegativeNumber() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            calculator.calculateSquareRoot(-4.0);
        });
        
        String expectedMessage = "Cannot calculate square root of a negative number";
        String actualMessage = exception.getMessage();
        
        assertTrue(actualMessage.contains(expectedMessage));
    }
    
    @Test
    public void testCalculatePower() {
        assertEquals(8.0, calculator.calculatePower(2.0, 3.0), 0.0001);
        assertEquals(1.0, calculator.calculatePower(5.0, 0.0), 0.0001);
        assertEquals(0.25, calculator.calculatePower(2.0, -2.0), 0.0001);
        assertEquals(0.0, calculator.calculatePower(0.0, 5.0), 0.0001);
        assertEquals(1.0, calculator.calculatePower(0.0, 0.0), 0.0001); // IEEE 754 standard
    }
    
    @Test
    public void testCalculatePercentage() {
        assertEquals(20.0, calculator.calculatePercentage(200.0, 10.0), 0.0001);
        assertEquals(0.0, calculator.calculatePercentage(100.0, 0.0), 0.0001);
        assertEquals(0.0, calculator.calculatePercentage(0.0, 50.0), 0.0001);
        assertEquals(150.0, calculator.calculatePercentage(100.0, 150.0), 0.0001);
        assertEquals(-5.0, calculator.calculatePercentage(-100.0, 5.0), 0.0001);
    }
    
    @Test
    public void testCalculateAbsoluteValue() {
        assertEquals(5.0, calculator.calculateAbsoluteValue(5.0), 0.0001);
        assertEquals(5.0, calculator.calculateAbsoluteValue(-5.0), 0.0001);
        assertEquals(0.0, calculator.calculateAbsoluteValue(0.0), 0.0001);
        assertEquals(3.5, calculator.calculateAbsoluteValue(-3.5), 0.0001);
    }
    
    @Test
    public void testRoundToDecimalPlaces() {
        assertEquals(3.14, calculator.roundToDecimalPlaces(3.14159, 2), 0.0001);
        assertEquals(3.142, calculator.roundToDecimalPlaces(3.14159, 3), 0.0001);
        assertEquals(3.0, calculator.roundToDecimalPlaces(3.14159, 0), 0.0001);
        assertEquals(10.0, calculator.roundToDecimalPlaces(9.99999, 0), 0.0001);
    }
    
    @Test
    public void testRoundToDecimalPlacesWithNegativeDecimalPlaces() {
        Exception exception = assertThrows(IllegalArgumentException.class, () -> {
            calculator.roundToDecimalPlaces(3.14159, -2);
        });
        
        String expectedMessage = "Decimal places must be non-negative";
        String actualMessage = exception.getMessage();
        
        assertTrue(actualMessage.contains(expectedMessage));
    }
}

// Made with Bob
