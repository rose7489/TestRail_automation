package com.calculator.app;

import java.util.Scanner;

/**
 * Main application class that provides a command-line interface for the Calculator.
 */
public class CalculatorApp {

    private static final Calculator calculator = new Calculator();
    private static final Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        System.out.println("Welcome to Simple Calculator App!");
        System.out.println("--------------------------------");
        
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
    
    private static void printMenu() {
        System.out.println("\nPlease select an operation:");
        System.out.println("1. Addition");
        System.out.println("2. Subtraction");
        System.out.println("3. Multiplication");
        System.out.println("4. Division");
        System.out.println("5. Exit");
        System.out.print("Enter your choice (1-5): ");
    }
    
    private static int getMenuChoice() {
        try {
            int choice = Integer.parseInt(scanner.nextLine());
            return choice;
        } catch (NumberFormatException e) {
            return -1; // Invalid choice
        }
    }
    
    private static void performAddition() {
        System.out.println("\n--- Addition ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.add(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f + %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
    private static void performSubtraction() {
        System.out.println("\n--- Subtraction ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.subtract(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f - %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
    private static void performMultiplication() {
        System.out.println("\n--- Multiplication ---");
        double[] numbers = getTwoNumbers();
        double result = calculator.multiply(numbers[0], numbers[1]);
        System.out.printf("Result: %.2f * %.2f = %.2f%n", numbers[0], numbers[1], result);
    }
    
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
    
    private static double[] getTwoNumbers() {
        double[] numbers = new double[2];
        
        System.out.print("Enter first number: ");
        numbers[0] = getNumberInput();
        
        System.out.print("Enter second number: ");
        numbers[1] = getNumberInput();
        
        return numbers;
    }
    
    private static double getNumberInput() {
        while (true) {
            try {
                return Double.parseDouble(scanner.nextLine());
            } catch (NumberFormatException e) {
                System.out.print("Invalid input. Please enter a number: ");
            }
        }
    }
}

// Made with Bob
