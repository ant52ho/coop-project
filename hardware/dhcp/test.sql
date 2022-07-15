/* To run: go to sqlite run query in command palette*/

SELECT * from maps;

SELECT id from maps;

SELECT MAX(mac) from test;

/*
INSERT INTO maps (id, mac, ip, hostname, subnet, serial) VALUES (7, "aa:bb:cc:dd:ee", "10.0.0.7" ,NULL, "10.0.0.0/24", 0);
*/
select * from maps;

-- Case-insensitive MAC-lookups may be handled in-database using either of the following methods:
--  - Put "COLLATE NOCASE" in the column-definition in maps:mac
--  - Include the following index

/*
delete from maps where ip not like "10.0%";

SELECT MIN(ip) from maps;
*/


/*
insert into maps (
id, mac, ip, hostname, subnet, serial)
values (
"testmac", "testip", Null, "testsubnet", "testserial");
*/