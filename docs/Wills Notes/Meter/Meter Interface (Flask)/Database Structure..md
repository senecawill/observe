
-- senecameter.Customers definition CREATE TABLE Customers ( customer_id int NOT NULL AUTO_INCREMENT, name varchar(100) NOT NULL, address_line1 varchar(255) DEFAULT NULL, address_line2 varchar(255) DEFAULT NULL, address_line3 varchar(255) DEFAULT NULL, city varchar(100) DEFAULT NULL, state_province varchar(100) DEFAULT NULL, country varchar(100) DEFAULT NULL, postal_code varchar(20) DEFAULT NULL, county_region varchar(100) DEFAULT NULL, contact_number varchar(15) DEFAULT NULL, email varchar(100) DEFAULT NULL, contact_person varchar(100) DEFAULT NULL, created_at datetime DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (customer_id) ) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.Customers example data
1	Berry Energy	310 Stiles Street			Clarksburg	WV	USA	26301	Lewis	+1-304-266-1308	dberry@berryenergy.com	David Berry	2024-01-04 04:34:49

-- senecameter.Devices definition CREATE TABLE Devices ( device_id varchar(50) NOT NULL, customer_id int DEFAULT NULL, device_name varchar(100) DEFAULT NULL, well_tender int DEFAULT NULL, type enum('Orifice Meter','Orifice Meter with Tank') DEFAULT NULL, installation_date date DEFAULT NULL, latitude double DEFAULT NULL, longitude double DEFAULT NULL, location_description varchar(255) DEFAULT NULL, status enum('active','maintenance','decommissioned') DEFAULT 'active', software_version varchar(50) DEFAULT NULL, hardware_version varchar(50) DEFAULT NULL, PRIMARY KEY (device_id), KEY Devices_device_id_IDX (device_id) USING BTREE, KEY customer_id (customer_id), KEY well_tender (well_tender), CONSTRAINT Devices_ibfk_1 FOREIGN KEY (customer_id) REFERENCES Customers (customer_id) ON DELETE SET NULL, CONSTRAINT Devices_ibfk_2 FOREIGN KEY (well_tender) REFERENCES Users (user_id) ON DELETE SET NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.Devices example data
dev:864049051634238	1	B1030M	1	Orifice Meter	2024-01-15	39.24063750000001	-80.38757421875	Rt. 19 N. of Clarksburg, on Right, just past Laurel Park Road	active		

-- senecameter.EventData definition CREATE TABLE EventData ( id int NOT NULL AUTO_INCREMENT, event_id varchar(50) NOT NULL, diff_adc double DEFAULT NULL, diff_pressure double DEFAULT NULL, mcfd double DEFAULT NULL, node_id varchar(36) DEFAULT NULL, press_adc double DEFAULT NULL, pressure double DEFAULT NULL, read_date date DEFAULT NULL, read_time time DEFAULT NULL, PRIMARY KEY (id), KEY EventData_Id_IDX (id) USING BTREE, KEY event_id (event_id), KEY EventData_read_date_IDX (read_date) USING BTREE, KEY EventData_read_time_IDX (read_time) USING BTREE, CONSTRAINT EventData_ibfk_1 FOREIGN KEY (event_id) REFERENCES Events (event_id) ON DELETE CASCADE ) ENGINE=InnoDB AUTO_INCREMENT=1797035 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.EventData example data
3229	c761db23-3fde-4a60-8fd7-b13375d52972	4205.0	0.61	1.74	832E79AD	5397.0	15.8	2024-01-15	09:00:05

-- senecameter.Events definition CREATE TABLE Events ( event_id varchar(36) NOT NULL, device_id varchar(50) NOT NULL, session varchar(36) DEFAULT NULL, best_id varchar(36) DEFAULT NULL, sn varchar(36) DEFAULT NULL, product varchar(100) DEFAULT NULL, app varchar(100) DEFAULT NULL, received double DEFAULT NULL, req varchar(50) DEFAULT NULL, event_time bigint DEFAULT NULL, file varchar(50) DEFAULT NULL, best_location_type varchar(50) DEFAULT NULL, best_location_when bigint DEFAULT NULL, best_lat double DEFAULT NULL, best_lon double DEFAULT NULL, best_location varchar(100) DEFAULT NULL, best_country varchar(50) DEFAULT NULL, best_timezone varchar(50) DEFAULT NULL, tower_when bigint DEFAULT NULL, tower_lat double DEFAULT NULL, tower_lon double DEFAULT NULL, tower_country varchar(50) DEFAULT NULL, tower_location varchar(100) DEFAULT NULL, tower_timezone varchar(50) DEFAULT NULL, tower_id varchar(50) DEFAULT NULL, fleets text, PRIMARY KEY (event_id), KEY Events_event_id_IDX (event_id) USING BTREE, KEY device_id (device_id), CONSTRAINT Events_ibfk_1 FOREIGN KEY (device_id) REFERENCES Devices (device_id) ON DELETE CASCADE ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.Events example data
c761db23-3fde-4a60-8fd7-b13375d52972	dev:864049051634238	d42942db-5e71-4fc5-ad37-acd9ef64f5c4	832E79AD	832E79AD	product:com.senecatechnologies.will:seneca_meter	app:d71fc34f-3ad9-497e-b843-dc8ab00a2a0e	1705330227.590482	note.add	1705328128	seneca6.qo	gps	1705325590	39.23430250000001	-80.39669921875	West Milford WV	US	America/New_York	1705330226	39.270962499999996	-80.370046875	US	Clarksburg WV	America/New_York	310,410,5898,90614026	fleet:eebb5cb4-3127-4615-824d-59bb59f64564

-- senecameter.Roles definition CREATE TABLE Roles ( role_id int NOT NULL AUTO_INCREMENT, role_name varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL, PRIMARY KEY (role_id), UNIQUE KEY role_name (role_name) ) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.Roles example data
1	admin
2	customer_admin
3	customer_user

-- senecameter.UserRoles definition CREATE TABLE UserRoles ( id int NOT NULL AUTO_INCREMENT, user_email varchar(100) NOT NULL, role_name varchar(255) NOT NULL, PRIMARY KEY (id), KEY UserRoles_ibfk_1 (user_email), KEY UserRoles_ibfk_2 (role_name), CONSTRAINT UserRoles_ibfk_1 FOREIGN KEY (user_email) REFERENCES Users (email) ON DELETE CASCADE, CONSTRAINT UserRoles_ibfk_2 FOREIGN KEY (role_name) REFERENCES Roles (role_name) ON DELETE CASCADE ) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; 

-- senecameter.UserRoles example data
4	admin@customer.com	customer_admin

-- senecameter.Users definition CREATE TABLE Users ( user_id int NOT NULL AUTO_INCREMENT, username varchar(50) NOT NULL, password_hash varchar(255) NOT NULL, email varchar(100) NOT NULL, role enum('admin','customer_user') NOT NULL, customer_id int DEFAULT NULL, created_at datetime DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (user_id), UNIQUE KEY username (username), UNIQUE KEY email (email), KEY customer_id (customer_id), CONSTRAINT Users_ibfk_1 FOREIGN KEY (customer_id) REFERENCES Customers (customer_id) ON DELETE SET NULL ) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci; ask me any questions you may have as we go through the process. 

-- senecameter.Users example data
17	admin	$2b$10$1n6ThBBzuapF7vTIBjPX8eKRN5KHosFoQ1mLVF5O2X8Qq6xT1Mciq	admin@admin.com	admin		2024-02-20 00:24:29

-- senecameter.monthly_production source

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `monthly_production` AS
select
    `e`.`device_id` AS `device_id`,
    `d`.`device_name` AS `device_name`,
    date_format(concat(`ed`.`read_date`, ' ', `ed`.`read_time`), '%Y-%m-%d %H') AS `datetime_hour`,
    date_format(from_unixtime(`e`.`event_time`), '%Y-%m-%d %H') AS `event_datetime_hour`,
    avg(`ed`.`diff_adc`) AS `avg_diff_adc`,
    avg(`ed`.`diff_pressure`) AS `avg_diff_pressure`,
    avg(`ed`.`mcfd`) AS `avg_mcfd`,
    min(`ed`.`node_id`) AS `node_id`,
    avg(`ed`.`press_adc`) AS `avg_press_adc`,
    avg(`ed`.`pressure`) AS `avg_pressure`
from
    ((`Devices` `d`
join `Events` `e` on
    ((`d`.`device_id` = `e`.`device_id`)))
join `EventData` `ed` on
    ((`e`.`event_id` = `ed`.`event_id`)))
group by
    `e`.`device_id`,
    date_format(concat(`ed`.`read_date`, ' ', `ed`.`read_time`), '%Y-%m-%d %H'),
    date_format(from_unixtime(`e`.`event_time`), '%Y-%m-%d %H');
    
-- senecameter.monthly_volume_24_month source

CREATE OR REPLACE
ALGORITHM = UNDEFINED VIEW `monthly_volume_24_month` AS with `device_list` as (
select
    distinct `Devices`.`device_id` AS `device_id`,
    `Devices`.`device_name` AS `device_name`
from
    `Devices`
where
    (`Devices`.`status` = 'active')),
`month_days` as (with recursive `months` as (
select
    date_format(curdate(), '%Y-%m-01') AS `date_val`
union all
select
    (`months`.`date_val` - interval 1 month) AS `date_val`
from
    `months`
where
    (`months`.`date_val` > (curdate() - interval 23 month)))
select
    year(`months`.`date_val`) AS `year`,
    month(`months`.`date_val`) AS `month`,
    dayofmonth(last_day(`months`.`date_val`)) AS `days_in_month`
from
    `months`)
select
    `d`.`device_id` AS `device_id`,
    `d`.`device_name` AS `device_name`,
    year(from_unixtime(`e`.`event_time`)) AS `year`,
    month(from_unixtime(`e`.`event_time`)) AS `month`,
    avg(coalesce(`ed`.`mcfd`, 0)) AS `avg_up_mcfd`,
    ((count(distinct date_format(from_unixtime(`e`.`event_time`), '%Y-%m-%d %H')) / (`md`.`days_in_month` * 24)) * 100) AS `uptime_percentage`,
    (avg(coalesce(`ed`.`mcfd`, 0)) * (count(distinct date_format(from_unixtime(`e`.`event_time`), '%Y-%m-%d %H')) / (`md`.`days_in_month` * 24))) AS `daily_mcfd`,
    ((avg(coalesce(`ed`.`mcfd`, 0)) * `md`.`days_in_month`) * (count(distinct date_format(from_unixtime(`e`.`event_time`), '%Y-%m-%d %H')) / (`md`.`days_in_month` * 24))) AS `total_mcf`
from
    (((`device_list` `d`
join `Events` `e` on
    ((`e`.`device_id` = `d`.`device_id`)))
join `EventData` `ed` on
    ((`ed`.`event_id` = `e`.`event_id`)))
join `month_days` `md` on
    (((`md`.`year` = year(from_unixtime(`e`.`event_time`)))
        and (`md`.`month` = month(from_unixtime(`e`.`event_time`))))))
where
    ((from_unixtime(`e`.`event_time`) >= (curdate() - interval 12 month))
        and (from_unixtime(`e`.`event_time`) < curdate()))
group by
    `d`.`device_id`,
    `d`.`device_name`,
    year(from_unixtime(`e`.`event_time`)),
    month(from_unixtime(`e`.`event_time`)),
    `md`.`days_in_month`
order by
    `d`.`device_name`,
    `year`,
    `month`;