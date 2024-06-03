This is Week 2 of Data with Danny [SQL Chalenge problems](https://8weeksqlchallenge.com/case-study-2/)

***PART A. Pizza Metrics***
**1 -- How many pizzas were ordered? (Assumption - including cancelled orders)**

    SELECT COUNT(pizza_id) as total_pizzas_ordered
    FROM pizza_runner.customer_orders;

| total_pizzas_ordered |
| -------------------- |
| 14                   |

---
**2 -- How many unique customer orders were made? (ONLY FULFILLED ORDERS)**

    SELECT COUNT(DISTINCT co.order_id) as total_orders
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.runner_orders as ro
    ON co.order_id = ro.order_id
    WHERE (cancellation IS NULL AND pickup_time IS NOT NULL) 
       OR (cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'));

| total_orders |
| ------------ |
| 8            |

---
**#3 -- How many successful orders were delivered by each runner?**
*Cancellation column contains a lot of missing values. It is not clear from the assignment, but I am assumning that the order is "sucsessful" 
if pick up time and distance are not nulls, even if the Cancellation is Null/NaN*

    SELECT runner_id as runner, COUNT(distinct order_id) as total_orders_delivered
    FROM pizza_runner.runner_orders
    WHERE (cancellation IS NULL AND pickup_time IS NOT NULL) OR (cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'))
    GROUP BY runner
    ORDER BY runner;

| runner | total_orders_delivered |
| ------ | ---------------------- |
| 1      | 4                      |
| 2      | 3                      |
| 3      | 1                      |

---
**#4 -- How many of each type of pizza was delivered?**

    SELECT pizza_name, COUNT(ro.order_id) as times_delivered
    FROM pizza_runner.runner_orders as ro
    LEFT JOIN pizza_runner.customer_orders  as co 
    ON ro.order_id = co.order_id
    LEFT JOIN pizza_runner.pizza_names as pn
    ON co.pizza_id = pn.pizza_id
    WHERE (cancellation IS NULL AND pickup_time IS NOT NULL) OR (cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'))
    GROUP BY pizza_name;

| pizza_name | times_delivered |
| ---------- | --------------- |
| Meatlovers | 9               |
| Vegetarian | 3               |

---
**#5 -- How many Vegetarian and Meatlovers were ordered by each customer? (includes cancelled orders)**

    SELECT customer_id, pizza_name, COUNT(*)
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.pizza_names AS pn
    ON co.pizza_id = pn.pizza_id
    GROUP BY customer_id, pizza_name
    ORDER BY customer_id;

| customer_id | pizza_name | count |
| ----------- | ---------- | ----- |
| 101         | Meatlovers | 2     |
| 101         | Vegetarian | 1     |
| 102         | Meatlovers | 2     |
| 102         | Vegetarian | 1     |
| 103         | Meatlovers | 3     |
| 103         | Vegetarian | 1     |
| 104         | Meatlovers | 3     |
| 105         | Vegetarian | 1     |

---
**#6 -- What was the maximum number of pizzas delivered in a single order?**

    SELECT ro.order_id, COUNT(*) as max_pizzas
    FROM  pizza_runner.runner_orders as ro
    FULL JOIN  pizza_runner.customer_orders as co
    ON ro.order_id = co.order_id
    GROUP BY ro.order_id
    ORDER BY max_pizzas DESC
    LIMIT 1;

| order_id | max_pizzas |
| -------- | ---------- |
| 4        | 3          |

---
**#7 -- What was the total volume of pizzas ordered for each hour of the day?**

    SELECT EXTRACT(HOUR FROM order_time) as order_hour, COUNT(pizza_id) number_of_pizzas_ordered
    FROM pizza_runner.customer_orders
    GROUP BY order_hour
    ORDER BY number_of_pizzas_ordered DESC;

| order_hour | number_of_pizzas_ordered |
| ---------- | ------------------------ |
| 18         | 3                        |
| 23         | 3                        |
| 21         | 3                        |
| 13         | 3                        |
| 11         | 1                        |
| 19         | 1                        |

---
**#8 -- What was the volume of orders for each day of the week?**

    SELECT EXTRACT(DOW FROM order_time) as order_day_of_the_week, COUNT(pizza_id) number_of_pizzas_ordered
    FROM pizza_runner.customer_orders
    GROUP BY order_day_of_the_week
    ORDER BY number_of_pizzas_ordered DESC;

| order_day_of_the_week | number_of_pizzas_ordered |
| --------------------- | ------------------------ |
| 3                     | 5                        |
| 6                     | 5                        |
| 4                     | 3                        |
| 5                     | 1                        |

---
***Part B. Runner and Customer Experience***
**#9 -- How many runners signed up for each 1 week period? (i.e. week starts 2021-01-01)**

    SELECT EXTRACT(WEEK from registration_date) as week_regisrered, COUNT(DISTINCT runner_id)
    FROM pizza_runner.runners 
    GROUP BY week_regisrered
    ORDER BY week_regisrered;

| week_regisrered | count |
| --------------- | ----- |
| 1               | 1     |
| 2               | 1     |
| 53              | 2     |

---
**#10 -- What was the average time in minutes it took for each runner to arrive at the Pizza Runner HQ to pickup the order?
-- We will assume the time that it took the runner to arrive is the difference between order date and pickup time**

    SELECT runner_id as runner, 
    AVG((EXTRACT(EPOCH from to_timestamp(pickup_time, 'YYYY-MM-DD HH24:MI:SS')) - EXTRACT(EPOCH from order_time))/60) as avg_minutes 
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.runner_orders as ro
    ON ro.order_id = co.order_id
    WHERE (cancellation IS NULL AND pickup_time IS NOT NULL) OR (cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'))
    GROUP BY runner
    ORDER BY avg_minutes DESC;

| runner | avg_minutes        |
| ------ | ------------------ |
| 2      | 23.720000000000002 |
| 1      | 15.677777777777777 |
| 3      | 10.466666666666667 |

---
**#11 -- What was the average distance travelled for each customer?**

    SELECT co.customer_id as customer, AVG((REGEXP_REPLACE(distance, '[[:alpha:]]', '', 'g'))::numeric) AS avg_distance
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.runner_orders as ro
    ON ro.order_id = co.order_id
    WHERE (cancellation IS NULL AND pickup_time IS NOT NULL) OR (cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'))
    GROUP BY customer
    ORDER BY avg_distance DESC;

| customer | avg_distance        |
| -------- | ------------------- |
| 105      | 25.0000000000000000 |
| 103      | 23.4000000000000000 |
| 101      | 20.0000000000000000 |
| 102      | 16.7333333333333333 |
| 104      | 10.0000000000000000 |

---

[View on DB Fiddle](https://www.db-fiddle.com/f/7VcQKQwsS3CTkGRFG7vu98/65)
