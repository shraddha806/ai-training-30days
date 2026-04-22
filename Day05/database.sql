DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS employees;

--CREATE TABLES
CREATE TABLE employees (
    emp_id INT PRIMARY KEY,
    name VARCHAR(50),
    department VARCHAR(50),
    city VARCHAR(50),
    salary INT,
    join_date DATE
);

CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    emp_id INT,
    product VARCHAR(50),
    amount INT,
    order_date DATE
);

-- INSERT DATA

INSERT INTO employees VALUES
(1, 'Amit', 'Engineering', 'Bangalore', 60000, '2023-05-10'),
(2, 'Priya', 'HR', 'Mumbai', 40000, '2022-03-15'),
(3, 'Rahul', 'Engineering', 'Pune', 80000, '2024-01-20'),
(4, 'Sneha', 'Finance', 'Chennai', 50000, '2021-07-25'),
(5, 'Kiran', 'Engineering', 'Bangalore', 75000, '2024-02-10');


INSERT INTO orders VALUES
(1, 1, 'Laptop', 50000, '2024-01-10'),
(2, 2, 'Mouse', 2000, '2024-02-15'),
(3, 1, 'Keyboard', 3000, '2024-03-05'),
(4, 3, 'Laptop', 55000, '2024-03-20'),
(5, 5, 'Monitor', 15000, '2024-04-01');

-- 1. Employees in Engineering (sorted by salary)
SELECT * 
FROM employees
WHERE department = 'Engineering'
ORDER BY salary DESC;

-- 2. Count employees per department
SELECT department, COUNT(*) AS total_employees
FROM employees
GROUP BY department;

-- 3. Top 3 highest-paid employees
SELECT *
FROM employees
ORDER BY salary DESC
LIMIT 3;

-- 4. Employees joined in 2024 or later
SELECT *
FROM employees
WHERE join_date >= '2024-01-01';

-- 5. Average salary by city
SELECT city, AVG(salary) AS avg_salary
FROM employees
GROUP BY city;

-- 6. List all orders with employee name (INNER JOIN)
SELECT e.name, o.product, o.amount, o.order_date
FROM employees e
INNER JOIN orders o ON e.emp_id = o.emp_id;

-- 7. Total revenue per employee
SELECT e.name, SUM(o.amount) AS total_revenue
FROM employees e
JOIN orders o ON e.emp_id = o.emp_id
GROUP BY e.name;

-- 8. Employees who never placed an order
SELECT e.name
FROM employees e
LEFT JOIN orders o ON e.emp_id = o.emp_id
WHERE o.emp_id IS NULL;

-- 9. Orders above 10,000 grouped by product
SELECT product, SUM(amount) AS total_amount
FROM orders
WHERE amount > 10000
GROUP BY product;

-- 10. Top 3 cities by total order amount
SELECT e.city, SUM(o.amount) AS total_amount
FROM employees e
JOIN orders o ON e.emp_id = o.emp_id
GROUP BY e.city
ORDER BY total_amount DESC
LIMIT 3;

-- PART B 
-- Rank employees by total spend
SELECT e.name,
       SUM(o.amount) AS total_spent,
       RANK() OVER (ORDER BY SUM(o.amount) DESC) AS rank
FROM employees e
JOIN orders o ON e.emp_id = o.emp_id
GROUP BY e.name;

-- Employees whose spend > 2x average
SELECT e.name, SUM(o.amount) AS total_spent
FROM employees e
JOIN orders o ON e.emp_id = o.emp_id
GROUP BY e.name
HAVING SUM(o.amount) > 2 * (
    SELECT AVG(amount) FROM orders
);