package com.calculator.app;

import java.util.Scanner;

/**
 * Main application class that provides a command-line interface for the Calculator.
 * This class handles user input, displays the menu of available operations,
 * and calls the appropriate Calculator methods based on user selection.
 */
public class CalculatorApp {

    private static final Calculator calculator = new Calculator();
    private static final Scanner scanner = new Scanner(System.in);

    /**
     * Main method that runs the calculator application.
     *
     * @param args command line arguments (not used)
     */
    public static void main(String[] args) {
        System.out.println("Welcome to Advanced Calculator App!");
        System.out.println("----------------------------------");
        
        boolean running = true;
        
        while (running) {
            printMenu();
            int choice = getMenuChoice();
            
            switch (choice) {
                case 1:
                    performAddition();
                    break;
                case 2:
                    performSubtraction();
                    break;
                case 3:
                    performMultiplication();
                    break;
                case 4:
                    performDivision();
                    break;
                case 5:
                    performSquareRoot();
                    break;
                case 6:
                    performPowerCalculation();
                    break;
                case 7:
                    performPercentageCalculation();
                    break;
                case 8:
                    performAbsoluteValue();
                    break;
                case 9:
                    performRounding();
                    break;
                case 10:
                    running = false;
                    System.out.println("Thank you for using the Calculator App. Goodbye!");
                    break;
                default:
                    System.out.println("Invalid choice. Please try again.");
            }
            
            if (running) {
                System.out.println("\nPress Enter to continue...");
                scanner.nextLine(); // Wait for user to press Enter
            }
        }
        
        scanner.close();
    }
    
    /**
     * Displays the menu of available calculator operations.
     */
    private static void printMenu() {
        System.out.println("\nPlease select an operation:");
        System.out.println("1. Addition");
        System.out.println("2. Subtraction");
        System.out.println("3. Multiplication");
        System.out.println("4. Division");
        System.out.println("5. Square Root");
        System.out.println("6. Power Calculation");
        System.out.println("7. Percentage Calculation");
        System.out.println("8. Absolute Value");
        System.out.println("9. Round to Decimal Places");
        System.out.println("10. Exit");
        System.out.print("Enter your choice (1-10): ");
    }
    
    /**
     * Gets the user's menu choice.
     *
     * @return the user's choice as an integer, or -1 if input is invalid
     */
    private static int getMenuChoice() {
        try {
            int choice = Integer.parseInt(scanner.nextLine());
            return choice;
        } catch (NumberFormatException e) {
            return -1; // Invalid choice
        }
    }
    
    /**
     * Performs addition operation by getting two numbers from user input
     * and displaying the result.
     */
    private static void performAddition() {
        System.out.println("\n--- Addition ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.add(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f + %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
    /**
     * Performs subtraction operation by getting two numbers from user input
     * and displaying the result.
     */
    private static void performSubtraction() {
        System.out.println("\n--- Subtraction ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.subtract(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f - %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
    /**
     * Performs multiplication operation by getting two numbers from user input
     * and displaying the result.
     */
    private static void performMultiplication() {
        System.out.println("\n--- Multiplication ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.multiply(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f * %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
    /**
     * Performs division operation by getting two numbers from user input
     * and displaying the result. Handles division by zero errors.
     */
    private static void performDivision() {
        System.out.println("\n--- Division ---");
        double[] numbers = getTwoNumbers();
        try {
            double result = calculator.divide(numbers[0], numbers[1]);
            System.out.printf("Result: %.2f / %.2f = %.2f%n", numbers[0], numbers[1], result);
        } catch (ArithmeticException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
    
    /**
     * Performs square root calculation by getting a number from user input
     * and displaying the result. Handles negative number errors.
     */
    private static void performSquareRoot() {
        System.out.println("\n--- Square Root ---");
        System.out.print("Enter a number: ");
        double number = getNumberInput();
        
        try {
            double result = calculator.calculateSquareRoot(number);
            System.out.printf("Result: √%.2f = %.2f%n", number, result);
        } catch (IllegalArgumentException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
    
    /**
     * Performs power calculation by getting base and exponent from user input
     * and displaying the result.
     */
    private static void performPowerCalculation() {
        System.out.println("\n--- Power Calculation ---");
        System.out.print("Enter base number: ");
        double base = getNumberInput();
        
        System.out.print("Enter exponent: ");
        double exponent = getNumberInput();
        
        double result = calculator.calculatePower(base, exponent);
        System.out.printf("Result: %.2f^%.2f = %.2f%n", base, exponent, result);
    }
    
    /**
     * Performs percentage calculation by getting value and percentage from user input
     * and displaying the result.
     */
    private static void performPercentageCalculation() {
        System.out.println("\n--- Percentage Calculation ---");
        System.out.print("Enter value: ");
        double value = getNumberInput();
        
        System.out.print("Enter percentage: ");
        double percentage = getNumberInput();
        
        double result = calculator.calculatePercentage(value, percentage);
        System.out.printf("Result: %.2f%% of %.2f = %.2f%n", percentage, value, result);
    }
    
    /**
     * Performs absolute value calculation by getting a number from user input
     * and displaying the result.
     */
    private static void performAbsoluteValue() {
        System.out.println("\n--- Absolute Value ---");
        System.out.print("Enter a number: ");
        double number = getNumberInput();
        
        double result = calculator.calculateAbsoluteValue(number);
        System.out.printf("Result: |%.2f| = %.2f%n", number, result);
    }
    
    /**
     * Performs rounding to decimal places by getting a number and decimal places from user input
     * and displaying the result. Handles negative decimal places errors.
     */
    private static void performRounding() {
        System.out.println("\n--- Round to Decimal Places ---");
        System.out.print("Enter a number: ");
        double number = getNumberInput();
        
        System.out.print("Enter number of decimal places: ");
        int decimalPlaces = getIntegerInput();
        
        try {
            double result = calculator.roundToDecimalPlaces(number, decimalPlaces);
            System.out.printf("Result: %.6f rounded to %d decimal places = %.6f%n",
                             number, decimalPlaces, result);
        } catch (IllegalArgumentException e) {
            System.out.println("Error: " + e.getMessage());
        }
    }
    
    /**
     * Gets two numbers from user input.
     *
     * @return an array containing the two numbers entered by the user
     */
    private static double[] getTwoNumbers() {
        double[] numbers = new double[2];
        
        System.out.print("Enter first number: ");
        numbers[0] = getNumberInput();
        
        System.out.print("Enter second number: ");
        numbers[1] = getNumberInput();
        
        return numbers;
    }
    
    /**
     * Gets a valid double number from user input.
     *
     * @return the number entered by the user
     */
    private static double getNumberInput() {
        while (true) {
            try {
                return Double.parseDouble(scanner.nextLine());
            } catch (NumberFormatException e) {
                System.out.print("Invalid input. Please enter a number: ");
            }
        }
    }
    
    /**
     * Gets a valid integer from user input.
     *
     * @return the integer entered by the user
     */
    private static int getIntegerInput() {
        while (true) {
            try {
                return Integer.parseInt(scanner.nextLine());
            } catch (NumberFormatException e) {
                System.out.print("Invalid input. Please enter an integer: ");
            }
        }
    }
}

// Made with Bob
