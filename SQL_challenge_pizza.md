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

**Query #7 -- For each order, how many delivered pizzas had at least 1 change and how many had no changes?**

*Next two questions deal with empty cells, null and NaN values. I had to implement additional checks for empty strings, "null" as string to make the query work correctly. I was using PostgreSQL v15 to run my queries*

    SELECT order_id, 
           SUM(CASE
                   WHEN (exclusions IS NOT NULL AND exclusions != 'null' AND exclusions != '') 
                     OR (extras IS NOT NULL AND extras != 'null' AND extras != '') 
                   THEN 1
                   ELSE 0 
               END) as pizzas_with_changes,
           SUM(CASE
                   WHEN (exclusions IS NULL OR exclusions = 'null' OR exclusions = '') 
                     AND (extras IS NULL OR extras = 'null' OR extras = '') 
                   THEN 1
                   ELSE 0 
               END) as pizzas_without_changes
    FROM pizza_runner.customer_orders
    GROUP BY order_id
    ORDER BY order_id;

| order_id | pizzas_with_changes | pizzas_without_changes |
| -------- | ------------------- | ---------------------- |
| 1        | 0                   | 1                      |
| 2        | 0                   | 1                      |
| 3        | 0                   | 2                      |
| 4        | 3                   | 0                      |
| 5        | 1                   | 0                      |
| 6        | 0                   | 1                      |
| 7        | 1                   | 0                      |
| 8        | 0                   | 1                      |
| 9        | 1                   | 0                      |
| 10       | 1                   | 1                      |

---
**Query #8 - -- How many pizzas were delivered that had both exclusions and extras?**

    SELECT COUNT(*) as pizzas_with_changes
    FROM pizza_runner.customer_orders
    WHERE exclusions IS NOT NULL AND exclusions != 'null' AND exclusions != ''
      AND extras IS NOT NULL AND extras != 'null' AND extras != '';

| pizzas_with_changes |
| ------------------- |
| 2                   |

**#9 -- What was the total volume of pizzas ordered for each hour of the day?**

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
**#10 -- What was the volume of orders for each day of the week?**

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
**#1 -- How many runners signed up for each 1 week period? (i.e. week starts 2021-01-01)**

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
**#2 -- What was the average time in minutes it took for each runner to arrive at the Pizza Runner HQ to pickup the order?
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
**#3 -- What was the average distance travelled for each customer?**

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
***D. Pricing and Ratings***

**Query #1 If a Meat Lovers pizza costs $12 and Vegetarian costs $10 and there were no charges for changes - how much money has Pizza Runner made so far if there are no delivery fees?**

    SELECT SUM(
               CASE
                  WHEN pizza_name = 'Meatlovers' THEN 12
                  WHEN pizza_name = 'Vegetarian' THEN 10
                  ELSE 0
               END) as total_revenue
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.pizza_names as pn
    ON co.pizza_id = pn.pizza_id
    LEFT JOIN pizza_runner.runner_orders AS ro 
    ON ro.order_id = co.order_id
    WHERE (ro.cancellation IS NULL OR ro.cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'));

| total_revenue |
| ------------- |
| 138           |

---
**Query #2 What if there was an additional $1 charge for any pizza extras?**

    SELECT SUM(
               CASE
                  WHEN pizza_name = 'Meatlovers' THEN 12
                  WHEN pizza_name = 'Vegetarian' THEN 10
                  ELSE 0
               END 
               + 
               CASE 
                  WHEN extras IS NOT NULL AND extras != 'null' AND extras != '' 
                  THEN array_length(string_to_array(extras, ','), 1) 
                  ELSE 0 
               END
           ) as total_revenue_with_extras
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.pizza_names as pn
    ON co.pizza_id = pn.pizza_id
    LEFT JOIN pizza_runner.runner_orders AS ro 
    ON ro.order_id = co.order_id
    WHERE (ro.cancellation IS NULL OR ro.cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'));

| total_revenue_with_extras |
| ------------------------- |
| 142                       |


---
**Query #3 f a Meat Lovers pizza was $12 and Vegetarian $10 fixed prices with no cost for extras and each runner is paid $0.30 per kilometre traveled - how much money does Pizza Runner have left over after these deliveries?**

    SELECT (SUM(
               CASE
                  WHEN pizza_name = 'Meatlovers' THEN 12
                  WHEN pizza_name = 'Vegetarian' THEN 10
                  ELSE 0
               END)- (SUM(
                CASE
                    WHEN distance IS NOT NULL AND distance <> '' THEN (REGEXP_REPLACE(distance, '[[:alpha:]]', '', 'g'))::numeric
                    ELSE 0
                END
            ) * 0.3)) as total_revenue_minus_delivery
    FROM pizza_runner.customer_orders as co
    LEFT JOIN pizza_runner.pizza_names as pn
    ON co.pizza_id = pn.pizza_id
    LEFT JOIN pizza_runner.runner_orders AS ro 
    ON ro.order_id = co.order_id
    WHERE (ro.cancellation IS NULL OR ro.cancellation NOT IN ('Restaurant Cancellation', 'Customer Cancellation'));

| total_revenue_minus_delivery |
| ---------------------------- |
| 73.38                        |

---

[View on DB Fiddle](https://www.db-fiddle.com/f/7VcQKQwsS3CTkGRFG7vu98/65)
