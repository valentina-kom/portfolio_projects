## Danny's Diner
This is Week 1 of Data with Danny [SQL Chalenge problems](https://8weeksqlchallenge.com/case-study-1/)

We help Danny's Diner learn more about their customers, their favorite dishes and performance of their loyalty program.
Some results have duplicates (several values assigned to the same customer). We are not concerned with these, as if people come as a group and one customer picks up the bill, all orders are recorded under one customer. If in the future Danny wants more granular information, database schema could be updated with "number of guests in the party" measure.

**Query #1 What is the total amount each customer spent at the restaurant?**

    SELECT
    	s.customer_id,
        SUM(m.price) as total_spend
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu as m
    ON s.product_id = m.product_id
    GROUP BY customer_id
    ORDER BY total_spend DESC;

| customer_id | total_spend |
| ----------- | ----------- |
| A           | 76          |
| B           | 74          |
| C           | 36          |

---
**Query #2 How many days has each customer visited the restaurant?**

    SELECT customer_id, 
    	COUNT(DISTINCT order_date) as number_of_visits
    FROM dannys_diner.sales
    GROUP BY customer_id
    ORDER BY number_of_visits DESC;

| customer_id | number_of_visits |
| ----------- | ---------------- |
| B           | 6                |
| A           | 4                |
| C           | 2                |

---
**Query #3 What was the first item from the menu purchased by each customer?**

    WITH first_item AS (
      SELECT s.customer_id,
      order_date, 
      product_name, 
      ROW_NUMBER() OVER(PARTITION BY s.customer_id ORDER BY order_date) AS rnk
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu as mm
    ON s.product_id = mm.product_id)
    
    SELECT customer_id, product_name
    FROM first_item
    WHERE rnk = 1;

| customer_id | product_name |
| ----------- | ------------ |
| A           | curry        |
| B           | curry        |
| C           | ramen        |

---
**Query #4 What is the most purchased item on the menu and how many times was it purchased by all customers?**

    SELECT m.product_name, COUNT(s.product_id) as times_purchased
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu as m
    ON s.product_id = m.product_id
    GROUP BY product_name
    ORDER BY times_purchased DESC
    LIMIT 1;

| product_name | times_purchased |
| ------------ | --------------- |
| ramen        | 8               |

---
**Query #5 Which item was the most popular for each customer?**

    WITH ranked_items AS (SELECT 
                              s.customer_id, 
                              product_name, 
                              COUNT(s.product_id) as times_purchased,
                              RANK() OVER(PARTITION BY s.customer_id ORDER BY COUNT(s.product_id) DESC) AS rnk 
                              FROM dannys_diner.sales AS s 
                              LEFT JOIN dannys_diner.menu AS m ON s.product_id = m.product_id 
                              GROUP BY s.customer_id, m.product_name )
        
        SELECT customer_id, product_name, times_purchased
        FROM ranked_items
        WHERE rnk = 1;

| customer_id | product_name | times_purchased |
| ----------- | ------------ | --------------- |
| A           | ramen        | 3               |
| B           | ramen        | 2               |
| B           | curry        | 2               |
| B           | sushi        | 2               |
| C           | ramen        | 3               |

---
**Query #6 Which item was purchased first by the customer after they became a member?**

    WITH first_purchased AS (SELECT 
                          s.customer_id, 
                          product_name, 
                          RANK() OVER(PARTITION BY s.customer_id ORDER BY order_date ) AS first_purchase 
                          FROM dannys_diner.sales AS s 
                          LEFT JOIN dannys_diner.menu AS m ON s.product_id = m.product_id 
                          INNER JOIN dannys_diner.members as mm -- as we are only interested in members
                          ON mm.customer_id = s.customer_id
                          WHERE order_date >= join_date)
    
    SELECT customer_id, product_name AS first_purchase
    FROM first_purchased
    WHERE first_purchase = 1;

| customer_id | first_purchase |
| ----------- | -------------- |
| A           | curry          |
| B           | sushi          |

---
**Query #7  Which item was purchased just before the customer became a member?**

    WITH last_purchase AS (SELECT 
                              s.customer_id, 
                              product_name, 
                              RANK() OVER(PARTITION BY s.customer_id ORDER BY order_date DESC) AS last_purchase 
                              FROM dannys_diner.sales AS s 
                              LEFT JOIN dannys_diner.menu AS m ON s.product_id = m.product_id 
                              INNER JOIN dannys_diner.members as mm 
                              ON mm.customer_id = s.customer_id
                              WHERE order_date < join_date)
        
        SELECT customer_id, product_name AS last_purchase
        FROM last_purchase
        WHERE last_purchase = 1;

| customer_id | last_purchase |
| ----------- | ------------- |
| A           | sushi         |
| A           | curry         |
| B           | sushi         |


---
**Query #8 What is the total items and amount spent for each member before they became a member?**

    SELECT s.customer_id, SUM(price) as total_spend, COUNT(s.product_id) as total_products
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu AS m
    ON s.product_id = m.product_id
    INNER JOIN dannys_diner.members as mm
    ON s.customer_id = mm.customer_id
    WHERE s.order_date < join_date
    GROUP BY s.customer_id;

| customer_id | total_spend | total_products |
| ----------- | ----------- | -------------- |
| B           | 40          | 3              |
| A           | 25          | 2              |

---
**Query #9 If each $1 spent equates to 10 points and sushi has a 2x points multiplier - how many points would each customer have?**

    SELECT s.customer_id, SUM(CASE
    	WHEN m.product_name = 'sushi' THEN m.price*20
    	ELSE m.price*10
    	END) as total_points
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu as m
    ON s.product_id = m.product_id
    INNER JOIN dannys_diner.members as mm
    ON s.customer_id = mm.customer_id
    WHERE s.order_date >= mm.join_date
    GROUP BY s.customer_id;

| customer_id | total_points |
| ----------- | ------------ |
| B           | 440          |
| A           | 510          |

---
**Query #10 In the first week after a customer joins the program (including their join date) they earn 2x points on all items, not just sushi - how many points do customer A and B have at the end of January?**

    SELECT s.customer_id, SUM(m.price*20) as total_points
    FROM dannys_diner.sales as s
    LEFT JOIN dannys_diner.menu as m
    ON s.product_id = m.product_id
    INNER JOIN dannys_diner.members as mm
    ON s.customer_id = mm.customer_id
    WHERE s.order_date BETWEEN mm.join_date AND (mm.join_date + INTERVAL '6 days')
    GROUP BY s.customer_id
    HAVING s.customer_id = 'A' OR s.customer_id = 'B';

| customer_id | total_points |
| ----------- | ------------ |
| B           | 200          |
| A           | 1020         |

---

[View on DB Fiddle](https://www.db-fiddle.com/f/2rM8RAnq7h5LLDTzZiRWcd/138)
