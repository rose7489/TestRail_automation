package com.calculator.app;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

/**
 * Unit tests for the Calculator class.
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
}

// Made with Bob
