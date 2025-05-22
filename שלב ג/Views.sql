-- View 1: ?????? ??? ????
CREATE VIEW equipment_maintenance_view AS
SELECT 
    m.contract_id,
    e.equipment_id,
    e.name AS equipment_name,
    cj.service_date,
    cj.estimated_next_service,
    cj.cost,
    cj.description
FROM Maintenance m
JOIN Equipment e ON m.equipment_id = e.equipment_id
JOIN Contract_job cj ON m.contract_id = cj.contract_id
WHERE cj.service_name = 'maintenance';

-- View 2: ??????? ?????? ?? ??? ?????????
CREATE VIEW freelancer_services_view AS
SELECT 
    f.pId,
    p.firstname || ' ' || p.lastname AS full_name,
    cj.service_name,
    cj.service_date,
    cj.estimated_next_service,
    cj.cost
FROM freelancer f
JOIN person p ON f.pId = p.pId
JOIN Contract_job cj ON f.pId = cj.pId;

-- ?????? 1 ?? view 1:
SELECT equipment_name, COUNT(*) AS maintenance_count
FROM equipment_maintenance_view
GROUP BY equipment_name
ORDER BY maintenance_count DESC
LIMIT 5;

-- ?????? 2 ?? view 1:
SELECT service_date, SUM(cost) AS total_cost
FROM equipment_maintenance_view
GROUP BY service_date
ORDER BY service_date;

-- ?????? 1 ?? view 2:
SELECT full_name, COUNT(*) AS service_count
FROM freelancer_services_view
GROUP BY full_name
ORDER BY service_count DESC;

-- ?????? 2 ?? view 2:
SELECT service_name, AVG(cost) AS avg_cost
FROM freelancer_services_view
GROUP BY service_name
ORDER BY avg_cost DESC;
