# nuScenes dev-kit.
# Code written by Holger Caesar, 2018.

from typing import Dict, List

from nuscenes import NuScenes

train_detect = \
    ['carla-1001', 'carla-1002', 'carla-1003', 'carla-1004', 'carla-1006', 'carla-1007', 'carla-1008', 'carla-1009', 'carla-1011', 'carla-1012', 'carla-1013', 'carla-1014', 'carla-1016', 'carla-1017', 'carla-1018', 'carla-1019', 'carla-1021', 'carla-1022', 'carla-1023', 'carla-1024', 'carla-1026', 'carla-1027', 'carla-1028', 'carla-1029', 'carla-1031', 'carla-1032', 'carla-1033', 'carla-1034', 'carla-1036', 'carla-1037', 'carla-1038', 'carla-1039', 'carla-1041', 'carla-1042', 'carla-1043', 'carla-1044', 'carla-1046', 'carla-1047', 'carla-1048', 'carla-1049', 'carla-1051', 'carla-1052', 'carla-1053', 'carla-1054', 'carla-1056', 'carla-1057', 'carla-1058', 'carla-1059', 'carla-1061', 'carla-1062', 'carla-1063', 'carla-1064', 'carla-1066', 'carla-1067', 'carla-1068', 'carla-1069', 'carla-1071', 'carla-1072', 'carla-1073', 'carla-1074', 'carla-1076', 'carla-1077', 'carla-1078', 'carla-1079', 'carla-1081', 'carla-1082', 'carla-1083', 'carla-1084', 'carla-1086', 'carla-1087', 'carla-1088', 'carla-1089', 'carla-1091', 'carla-1092', 'carla-1093', 'carla-1094', 'carla-1096', 'carla-1097', 'carla-1098', 'carla-1099', 'carla-1101', 'carla-1102', 'carla-1103', 'carla-1104', 'carla-1106', 'carla-1107', 'carla-1108', 'carla-1109', 'carla-1111', 'carla-1112', 'carla-1113', 'carla-1114', 'carla-1116', 'carla-1117', 'carla-1118', 'carla-1119', 'carla-1121', 'carla-1122', 'carla-1123', 'carla-1124', 'carla-1126', 'carla-1127', 'carla-1128', 'carla-1129', 'carla-1131', 'carla-1132', 'carla-1133', 'carla-1134', 'carla-1136', 'carla-1137', 'carla-1138', 'carla-1139', 'carla-1141', 'carla-1142', 'carla-1143', 'carla-1144', 'carla-1146', 'carla-1147', 'carla-1148', 'carla-1149', 'carla-1151', 'carla-1152', 'carla-1153', 'carla-1154', 'carla-1156', 'carla-1157', 'carla-1158', 'carla-1159', 'carla-1161', 'carla-1162', 'carla-1163', 'carla-1164', 'carla-1166', 'carla-1167', 'carla-1168', 'carla-1169', 'carla-1171', 'carla-1172', 'carla-1173', 'carla-1174', 'carla-1176', 'carla-1177', 'carla-1178', 'carla-1179', 'carla-1181', 'carla-1182', 'carla-1183', 'carla-1184', 'carla-1186', 'carla-1187', 'carla-1188', 'carla-1189', 'carla-1191', 'carla-1192', 'carla-1193', 'carla-1194', 'carla-1196', 'carla-1197', 'carla-1198', 'carla-1199', 'carla-1201', 'carla-1202', 'carla-1203', 'carla-1204', 'carla-1206', 'carla-1207', 'carla-1208', 'carla-1209', 'carla-1211', 'carla-1212', 'carla-1213', 'carla-1214', 'carla-1216', 'carla-1217', 'carla-1218', 'carla-1219', 'carla-1221', 'carla-1222', 'carla-1223', 'carla-1224', 'carla-1226', 'carla-1227', 'carla-1228', 'carla-1229', 'carla-1231', 'carla-1232', 'carla-1233', 'carla-1234', 'carla-1236', 'carla-1237', 'carla-1238', 'carla-1239', 'carla-1241', 'carla-1242', 'carla-1243', 'carla-1244', 'carla-1246', 'carla-1247', 'carla-1248', 'carla-1249', 'carla-1251', 'carla-1252', 'carla-1253', 'carla-1254', 'carla-1256', 'carla-1257', 'carla-1258', 'carla-1259', 'carla-1261', 'carla-1262', 'carla-1263', 'carla-1264', 'carla-1266', 'carla-1267', 'carla-1268', 'carla-1269', 'carla-1271', 'carla-1272', 'carla-1273', 'carla-1274', 'carla-1276', 'carla-1277', 'carla-1278', 'carla-1279', 'carla-1281', 'carla-1282', 'carla-1283', 'carla-1284', 'carla-1286', 'carla-1287', 'carla-1288', 'carla-1289', 'carla-1291', 'carla-1292', 'carla-1293', 'carla-1294', 'carla-1296', 'carla-1297', 'carla-1298', 'carla-1299', 'carla-1301', 'carla-1302', 'carla-1303', 'carla-1304', 'carla-1306', 'carla-1307', 'carla-1308', 'carla-1309', 'carla-1311', 'carla-1312', 'carla-1313', 'carla-1314', 'carla-1316', 'carla-1317', 'carla-1318', 'carla-1319', 'carla-1321', 'carla-1322', 'carla-1323', 'carla-1324', 'carla-1326', 'carla-1327', 'carla-1328', 'carla-1329', 'carla-1331', 'carla-1332', 'carla-1333', 'carla-1334', 'carla-1336', 'carla-1337', 'carla-1338', 'carla-1339', 'carla-1341', 'carla-1342', 'carla-1343', 'carla-1344', 'carla-1346', 'carla-1347', 'carla-1348', 'carla-1349', 'carla-1351', 'carla-1352', 'carla-1353', 'carla-1354', 'carla-1356', 'carla-1357', 'carla-1358', 'carla-1359', 'carla-1361', 'carla-1362', 'carla-1363', 'carla-1364', 'carla-1366', 'carla-1367', 'carla-1368', 'carla-1369', 'carla-1371', 'carla-1372', 'carla-1373', 'carla-1374', 'carla-1376', 'carla-1377', 'carla-1378', 'carla-1379', 'carla-1381', 'carla-1382', 'carla-1383', 'carla-1384', 'carla-1386', 'carla-1387', 'carla-1388', 'carla-1389', 'carla-1391', 'carla-1392', 'carla-1393', 'carla-1394', 'carla-1396', 'carla-1397', 'carla-1398', 'carla-1399', 'carla-1401', 'carla-1402', 'carla-1403', 'carla-1404', 'carla-1406', 'carla-1407', 'carla-1408', 'carla-1409', 'carla-1411', 'carla-1412', 'carla-1413', 'carla-1414', 'carla-1416', 'carla-1417', 'carla-1418', 'carla-1419', 'carla-1421', 'carla-1422', 'carla-1423', 'carla-1424', 'carla-1426', 'carla-1427', 'carla-1428', 'carla-1429', 'carla-1431', 'carla-1432', 'carla-1433', 'carla-1434', 'carla-1436', 'carla-1437', 'carla-1438', 'carla-1439', 'carla-1441', 'carla-1442', 'carla-1443', 'carla-1444', 'carla-1446', 'carla-1447', 'carla-1448', 'carla-1449', 'carla-1451', 'carla-1452', 'carla-1453', 'carla-1454', 'carla-1456', 'carla-1457', 'carla-1458', 'carla-1459', 'carla-1461', 'carla-1462', 'carla-1463', 'carla-1464', 'carla-1466', 'carla-1467', 'carla-1468', 'carla-1469', 'carla-1471', 'carla-1472', 'carla-1473', 'carla-1474', 'carla-1476', 'carla-1477', 'carla-1478', 'carla-1479', 'carla-1481', 'carla-1482', 'carla-1483', 'carla-1484', 'carla-1486', 'carla-1487', 'carla-1488', 'carla-1489', 'carla-1491', 'carla-1492', 'carla-1493', 'carla-1494', 'carla-1496', 'carla-1497', 'carla-1498', 'carla-1499', 'carla-1501', 'carla-1502', 'carla-1503', 'carla-1504', 'carla-1506', 'carla-1507', 'carla-1508', 'carla-1509', 'carla-1511', 'carla-1512', 'carla-1513', 'carla-1514', 'carla-1516', 'carla-1517', 'carla-1518', 'carla-1519', 'carla-1521', 'carla-1522', 'carla-1523', 'carla-1524', 'carla-1526', 'carla-1527', 'carla-1528', 'carla-1529', 'carla-1531', 'carla-1532', 'carla-1533', 'carla-1534', 'carla-1536', 'carla-1537', 'carla-1538', 'carla-1539', 'carla-1541', 'carla-1542', 'carla-1543', 'carla-1544', 'carla-1546', 'carla-1547', 'carla-1548', 'carla-1549', 'carla-1551', 'carla-1552', 'carla-1553', 'carla-1554', 'carla-1556', 'carla-1557', 'carla-1558', 'carla-1559', 'carla-1561', 'carla-1562', 'carla-1563', 'carla-1564', 'carla-1566', 'carla-1567', 'carla-1568', 'carla-1569', 'carla-1571', 'carla-1572', 'carla-1573', 'carla-1574', 'carla-1576', 'carla-1577', 'carla-1578', 'carla-1579', 'carla-1581', 'carla-1582', 'carla-1583', 'carla-1584', 'carla-1586', 'carla-1587', 'carla-1588', 'carla-1589', 'carla-1591', 'carla-1592', 'carla-1593', 'carla-1594', 'carla-1596', 'carla-1597', 'carla-1598', 'carla-1599', 'carla-1601', 'carla-1602', 'carla-1603', 'carla-1604', 'carla-1606', 'carla-1607', 'carla-1608', 'carla-1609', 'carla-1611', 'carla-1612', 'carla-1613', 'carla-1614', 'carla-1616', 'carla-1617', 'carla-1618', 'carla-1619', 'carla-1621', 'carla-1622', 'carla-1623', 'carla-1624', 'carla-1626', 'carla-1627', 'carla-1628', 'carla-1629', 'carla-1631', 'carla-1632', 'carla-1633', 'carla-1634', 'carla-1636', 'carla-1637', 'carla-1638', 'carla-1639', 'carla-1641', 'carla-1642', 'carla-1643', 'carla-1644', 'carla-1646', 'carla-1647', 'carla-1648', 'carla-1649', 'carla-1651', 'carla-1652', 'carla-1653', 'carla-1654', 'carla-1656', 'carla-1657', 'carla-1658', 'carla-1659', 'carla-1661', 'carla-1662', 'carla-1663', 'carla-1664', 'carla-1666', 'carla-1667', 'carla-1668', 'carla-1669', 'carla-1671', 'carla-1672', 'carla-1673', 'carla-1674', 'carla-1676', 'carla-1677', 'carla-1678', 'carla-1679', 'carla-1681', 'carla-1682', 'carla-1683', 'carla-1684', 'carla-1686', 'carla-1687', 'carla-1688', 'carla-1689', 'carla-1691', 'carla-1692', 'carla-1693', 'carla-1694', 'carla-1696', 'carla-1697', 'carla-1698', 'carla-1699', 'carla-1701', 'carla-1702', 'carla-1703', 'carla-1704', 'carla-1706', 'carla-1707', 'carla-1708', 'carla-1709', 'carla-1711', 'carla-1712', 'carla-1713', 'carla-1714', 'carla-1716', 'carla-1717', 'carla-1718', 'carla-1719', 'carla-1721', 'carla-1722', 'carla-1723', 'carla-1724', 'carla-1726', 'carla-1727', 'carla-1728', 'carla-1729', 'carla-1731', 'carla-1732', 'carla-1733', 'carla-1734', 'carla-1736', 'carla-1737', 'carla-1738', 'carla-1739', 'carla-1741', 'carla-1742', 'carla-1743', 'carla-1744', 'carla-1746', 'carla-1747', 'carla-1748', 'carla-1749', 'carla-1751', 'carla-1752', 'carla-1753', 'carla-1754', 'carla-1756', 'carla-1757', 'carla-1758', 'carla-1759', 'carla-1761', 'carla-1762', 'carla-1763', 'carla-1764', 'carla-1766', 'carla-1767', 'carla-1768', 'carla-1769', 'carla-1771', 'carla-1772', 'carla-1773', 'carla-1774', 'carla-1776', 'carla-1777', 'carla-1778', 'carla-1779', 'carla-1781', 'carla-1782', 'carla-1783', 'carla-1784', 'carla-1786', 'carla-1787', 'carla-1788', 'carla-1789', 'carla-1791', 'carla-1792', 'carla-1793', 'carla-1794', 'carla-1796', 'carla-1797', 'carla-1798', 'carla-1799', 'carla-1801', 'carla-1802', 'carla-1803', 'carla-1804', 'carla-1806', 'carla-1807', 'carla-1808', 'carla-1809', 'carla-1811', 'carla-1812', 'carla-1813', 'carla-1814', 'carla-1816', 'carla-1817', 'carla-1818', 'carla-1819', 'carla-1821', 'carla-1822', 'carla-1823', 'carla-1824', 'carla-1826', 'carla-1827', 'carla-1828', 'carla-1829', 'carla-1831', 'carla-1832', 'carla-1833', 'carla-1834', 'carla-1836', 'carla-1837', 'carla-1838', 'carla-1839', 'carla-1841', 'carla-1842', 'carla-1843', 'carla-1844', 'carla-1846', 'carla-1847', 'carla-1848', 'carla-1849', 'carla-1851', 'carla-1852', 'carla-1853', 'carla-1854', 'carla-1856', 'carla-1857', 'carla-1858', 'carla-1859', 'carla-1861', 'carla-1862', 'carla-1863', 'carla-1864', 'carla-1866', 'carla-1867', 'carla-1868', 'carla-1869', 'carla-1871', 'carla-1872', 'carla-1873', 'carla-1874', 'carla-1876', 'carla-1877', 'carla-1878', 'carla-1879', 'carla-1881', 'carla-1882', 'carla-1883', 'carla-1884', 'carla-1886', 'carla-1887', 'carla-1888', 'carla-1889', 'carla-1891', 'carla-1892', 'carla-1893', 'carla-1894', 'carla-1896', 'carla-1897', 'carla-1898', 'carla-1899', 'carla-1901', 'carla-1902', 'carla-1903', 'carla-1904', 'carla-1906', 'carla-1907', 'carla-1908', 'carla-1909', 'carla-1911', 'carla-1912', 'carla-1913', 'carla-1914', 'carla-1916', 'carla-1917', 'carla-1918', 'carla-1919', 'carla-1921', 'carla-1922', 'carla-1923', 'carla-1924', 'carla-1926', 'carla-1927', 'carla-1928', 'carla-1929', 'carla-1931', 'carla-1932', 'carla-1933', 'carla-1934', 'carla-1936', 'carla-1937', 'carla-1938', 'carla-1939', 'carla-1941', 'carla-1942', 'carla-1943', 'carla-1944', 'carla-1946', 'carla-1947', 'carla-1948', 'carla-1949', 'carla-1951', 'carla-1952', 'carla-1953', 'carla-1954', 'carla-1956', 'carla-1957', 'carla-1958', 'carla-1959', 'carla-1961', 'carla-1962', 'carla-1963', 'carla-1964', 'carla-1966', 'carla-1967', 'carla-1968', 'carla-1969', 'carla-1971', 'carla-1972', 'carla-1973', 'carla-1974', 'carla-1976', 'carla-1977', 'carla-1978', 'carla-1979', 'carla-1981', 'carla-1982', 'carla-1983', 'carla-1984', 'carla-1986', 'carla-1987', 'carla-1988', 'carla-1989', 'carla-1991', 'carla-1992', 'carla-1993', 'carla-1994', 'carla-1996', 'carla-1997', 'carla-1998', 'carla-1999',
     'scene-0001', 'scene-0002', 'scene-0041', 'scene-0042', 'scene-0043', 'scene-0044', 'scene-0045', 'scene-0046',
     'scene-0047', 'scene-0048', 'scene-0049', 'scene-0050', 'scene-0051', 'scene-0052', 'scene-0053', 'scene-0054',
     'scene-0055', 'scene-0056', 'scene-0057', 'scene-0058', 'scene-0059', 'scene-0060', 'scene-0061', 'scene-0062',
     'scene-0063', 'scene-0064', 'scene-0065', 'scene-0066', 'scene-0067', 'scene-0068', 'scene-0069', 'scene-0070',
     'scene-0071', 'scene-0072', 'scene-0073', 'scene-0074', 'scene-0075', 'scene-0076', 'scene-0161', 'scene-0162',
     'scene-0163', 'scene-0164', 'scene-0165', 'scene-0166', 'scene-0167', 'scene-0168', 'scene-0170', 'scene-0171',
     'scene-0172', 'scene-0173', 'scene-0174', 'scene-0175', 'scene-0176', 'scene-0190', 'scene-0191', 'scene-0192',
     'scene-0193', 'scene-0194', 'scene-0195', 'scene-0196', 'scene-0199', 'scene-0200', 'scene-0202', 'scene-0203',
     'scene-0204', 'scene-0206', 'scene-0207', 'scene-0208', 'scene-0209', 'scene-0210', 'scene-0211', 'scene-0212',
     'scene-0213', 'scene-0214', 'scene-0254', 'scene-0255', 'scene-0256', 'scene-0257', 'scene-0258', 'scene-0259',
     'scene-0260', 'scene-0261', 'scene-0262', 'scene-0263', 'scene-0264', 'scene-0283', 'scene-0284', 'scene-0285',
     'scene-0286', 'scene-0287', 'scene-0288', 'scene-0289', 'scene-0290', 'scene-0291', 'scene-0292', 'scene-0293',
     'scene-0294', 'scene-0295', 'scene-0296', 'scene-0297', 'scene-0298', 'scene-0299', 'scene-0300', 'scene-0301',
     'scene-0302', 'scene-0303', 'scene-0304', 'scene-0305', 'scene-0306', 'scene-0315', 'scene-0316', 'scene-0317',
     'scene-0318', 'scene-0321', 'scene-0323', 'scene-0324', 'scene-0347', 'scene-0348', 'scene-0349', 'scene-0350',
     'scene-0351', 'scene-0352', 'scene-0353', 'scene-0354', 'scene-0355', 'scene-0356', 'scene-0357', 'scene-0358',
     'scene-0359', 'scene-0360', 'scene-0361', 'scene-0362', 'scene-0363', 'scene-0364', 'scene-0365', 'scene-0366',
     'scene-0367', 'scene-0368', 'scene-0369', 'scene-0370', 'scene-0371', 'scene-0372', 'scene-0373', 'scene-0374',
     'scene-0375', 'scene-0382', 'scene-0420', 'scene-0421', 'scene-0422', 'scene-0423', 'scene-0424', 'scene-0425',
     'scene-0426', 'scene-0427', 'scene-0428', 'scene-0429', 'scene-0430', 'scene-0431', 'scene-0432', 'scene-0433',
     'scene-0434', 'scene-0435', 'scene-0436', 'scene-0437', 'scene-0438', 'scene-0439', 'scene-0457', 'scene-0458',
     'scene-0459', 'scene-0461', 'scene-0462', 'scene-0463', 'scene-0464', 'scene-0465', 'scene-0467', 'scene-0468',
     'scene-0469', 'scene-0471', 'scene-0472', 'scene-0474', 'scene-0475', 'scene-0476', 'scene-0477', 'scene-0478',
     'scene-0479', 'scene-0480', 'scene-0566', 'scene-0568', 'scene-0570', 'scene-0571', 'scene-0572', 'scene-0573',
     'scene-0574', 'scene-0575', 'scene-0576', 'scene-0577', 'scene-0578', 'scene-0580', 'scene-0582', 'scene-0583',
     'scene-0665', 'scene-0666', 'scene-0667', 'scene-0668', 'scene-0669', 'scene-0670', 'scene-0671', 'scene-0672',
     'scene-0673', 'scene-0674', 'scene-0675', 'scene-0676', 'scene-0677', 'scene-0678', 'scene-0679', 'scene-0681',
     'scene-0683', 'scene-0684', 'scene-0685', 'scene-0686', 'scene-0687', 'scene-0688', 'scene-0689', 'scene-0739',
     'scene-0740', 'scene-0741', 'scene-0744', 'scene-0746', 'scene-0747', 'scene-0749', 'scene-0750', 'scene-0751',
     'scene-0752', 'scene-0757', 'scene-0758', 'scene-0759', 'scene-0760', 'scene-0761', 'scene-0762', 'scene-0763',
     'scene-0764', 'scene-0765', 'scene-0767', 'scene-0768', 'scene-0769', 'scene-0868', 'scene-0869', 'scene-0870',
     'scene-0871', 'scene-0872', 'scene-0873', 'scene-0875', 'scene-0876', 'scene-0877', 'scene-0878', 'scene-0880',
     'scene-0882', 'scene-0883', 'scene-0884', 'scene-0885', 'scene-0886', 'scene-0887', 'scene-0888', 'scene-0889',
     'scene-0890', 'scene-0891', 'scene-0892', 'scene-0893', 'scene-0894', 'scene-0895', 'scene-0896', 'scene-0897',
     'scene-0898', 'scene-0899', 'scene-0900', 'scene-0901', 'scene-0902', 'scene-0903', 'scene-0945', 'scene-0947',
     'scene-0949', 'scene-0952', 'scene-0953', 'scene-0955', 'scene-0956', 'scene-0957', 'scene-0958', 'scene-0959',
     'scene-0960', 'scene-0961', 'scene-0975', 'scene-0976', 'scene-0977', 'scene-0978', 'scene-0979', 'scene-0980',
     'scene-0981', 'scene-0982', 'scene-0983', 'scene-0984', 'scene-0988', 'scene-0989', 'scene-0990', 'scene-0991',
     'scene-1011', 'scene-1012', 'scene-1013', 'scene-1014', 'scene-1015', 'scene-1016', 'scene-1017', 'scene-1018',
     'scene-1019', 'scene-1020', 'scene-1021', 'scene-1022', 'scene-1023', 'scene-1024', 'scene-1025', 'scene-1074',
     'scene-1075', 'scene-1076', 'scene-1077', 'scene-1078', 'scene-1079', 'scene-1080', 'scene-1081', 'scene-1082',
     'scene-1083', 'scene-1084', 'scene-1085', 'scene-1086', 'scene-1087', 'scene-1088', 'scene-1089', 'scene-1090',
     'scene-1091', 'scene-1092', 'scene-1093', 'scene-1094', 'scene-1095', 'scene-1096', 'scene-1097', 'scene-1098',
     'scene-1099', 'scene-1100', 'scene-1101', 'scene-1102', 'scene-1104', 'scene-1105']

train_track = \
    ['scene-0004', 'scene-0005', 'scene-0006', 'scene-0007', 'scene-0008', 'scene-0009', 'scene-0010', 'scene-0011',
     'scene-0019', 'scene-0020', 'scene-0021', 'scene-0022', 'scene-0023', 'scene-0024', 'scene-0025', 'scene-0026',
     'scene-0027', 'scene-0028', 'scene-0029', 'scene-0030', 'scene-0031', 'scene-0032', 'scene-0033', 'scene-0034',
     'scene-0120', 'scene-0121', 'scene-0122', 'scene-0123', 'scene-0124', 'scene-0125', 'scene-0126', 'scene-0127',
     'scene-0128', 'scene-0129', 'scene-0130', 'scene-0131', 'scene-0132', 'scene-0133', 'scene-0134', 'scene-0135',
     'scene-0138', 'scene-0139', 'scene-0149', 'scene-0150', 'scene-0151', 'scene-0152', 'scene-0154', 'scene-0155',
     'scene-0157', 'scene-0158', 'scene-0159', 'scene-0160', 'scene-0177', 'scene-0178', 'scene-0179', 'scene-0180',
     'scene-0181', 'scene-0182', 'scene-0183', 'scene-0184', 'scene-0185', 'scene-0187', 'scene-0188', 'scene-0218',
     'scene-0219', 'scene-0220', 'scene-0222', 'scene-0224', 'scene-0225', 'scene-0226', 'scene-0227', 'scene-0228',
     'scene-0229', 'scene-0230', 'scene-0231', 'scene-0232', 'scene-0233', 'scene-0234', 'scene-0235', 'scene-0236',
     'scene-0237', 'scene-0238', 'scene-0239', 'scene-0240', 'scene-0241', 'scene-0242', 'scene-0243', 'scene-0244',
     'scene-0245', 'scene-0246', 'scene-0247', 'scene-0248', 'scene-0249', 'scene-0250', 'scene-0251', 'scene-0252',
     'scene-0253', 'scene-0328', 'scene-0376', 'scene-0377', 'scene-0378', 'scene-0379', 'scene-0380', 'scene-0381',
     'scene-0383', 'scene-0384', 'scene-0385', 'scene-0386', 'scene-0388', 'scene-0389', 'scene-0390', 'scene-0391',
     'scene-0392', 'scene-0393', 'scene-0394', 'scene-0395', 'scene-0396', 'scene-0397', 'scene-0398', 'scene-0399',
     'scene-0400', 'scene-0401', 'scene-0402', 'scene-0403', 'scene-0405', 'scene-0406', 'scene-0407', 'scene-0408',
     'scene-0410', 'scene-0411', 'scene-0412', 'scene-0413', 'scene-0414', 'scene-0415', 'scene-0416', 'scene-0417',
     'scene-0418', 'scene-0419', 'scene-0440', 'scene-0441', 'scene-0442', 'scene-0443', 'scene-0444', 'scene-0445',
     'scene-0446', 'scene-0447', 'scene-0448', 'scene-0449', 'scene-0450', 'scene-0451', 'scene-0452', 'scene-0453',
     'scene-0454', 'scene-0455', 'scene-0456', 'scene-0499', 'scene-0500', 'scene-0501', 'scene-0502', 'scene-0504',
     'scene-0505', 'scene-0506', 'scene-0507', 'scene-0508', 'scene-0509', 'scene-0510', 'scene-0511', 'scene-0512',
     'scene-0513', 'scene-0514', 'scene-0515', 'scene-0517', 'scene-0518', 'scene-0525', 'scene-0526', 'scene-0527',
     'scene-0528', 'scene-0529', 'scene-0530', 'scene-0531', 'scene-0532', 'scene-0533', 'scene-0534', 'scene-0535',
     'scene-0536', 'scene-0537', 'scene-0538', 'scene-0539', 'scene-0541', 'scene-0542', 'scene-0543', 'scene-0544',
     'scene-0545', 'scene-0546', 'scene-0584', 'scene-0585', 'scene-0586', 'scene-0587', 'scene-0588', 'scene-0589',
     'scene-0590', 'scene-0591', 'scene-0592', 'scene-0593', 'scene-0594', 'scene-0595', 'scene-0596', 'scene-0597',
     'scene-0598', 'scene-0599', 'scene-0600', 'scene-0639', 'scene-0640', 'scene-0641', 'scene-0642', 'scene-0643',
     'scene-0644', 'scene-0645', 'scene-0646', 'scene-0647', 'scene-0648', 'scene-0649', 'scene-0650', 'scene-0651',
     'scene-0652', 'scene-0653', 'scene-0654', 'scene-0655', 'scene-0656', 'scene-0657', 'scene-0658', 'scene-0659',
     'scene-0660', 'scene-0661', 'scene-0662', 'scene-0663', 'scene-0664', 'scene-0695', 'scene-0696', 'scene-0697',
     'scene-0698', 'scene-0700', 'scene-0701', 'scene-0703', 'scene-0704', 'scene-0705', 'scene-0706', 'scene-0707',
     'scene-0708', 'scene-0709', 'scene-0710', 'scene-0711', 'scene-0712', 'scene-0713', 'scene-0714', 'scene-0715',
     'scene-0716', 'scene-0717', 'scene-0718', 'scene-0719', 'scene-0726', 'scene-0727', 'scene-0728', 'scene-0730',
     'scene-0731', 'scene-0733', 'scene-0734', 'scene-0735', 'scene-0736', 'scene-0737', 'scene-0738', 'scene-0786',
     'scene-0787', 'scene-0789', 'scene-0790', 'scene-0791', 'scene-0792', 'scene-0803', 'scene-0804', 'scene-0805',
     'scene-0806', 'scene-0808', 'scene-0809', 'scene-0810', 'scene-0811', 'scene-0812', 'scene-0813', 'scene-0815',
     'scene-0816', 'scene-0817', 'scene-0819', 'scene-0820', 'scene-0821', 'scene-0822', 'scene-0847', 'scene-0848',
     'scene-0849', 'scene-0850', 'scene-0851', 'scene-0852', 'scene-0853', 'scene-0854', 'scene-0855', 'scene-0856',
     'scene-0858', 'scene-0860', 'scene-0861', 'scene-0862', 'scene-0863', 'scene-0864', 'scene-0865', 'scene-0866',
     'scene-0992', 'scene-0994', 'scene-0995', 'scene-0996', 'scene-0997', 'scene-0998', 'scene-0999', 'scene-1000',
     'scene-1001', 'scene-1002', 'scene-1003', 'scene-1004', 'scene-1005', 'scene-1006', 'scene-1007', 'scene-1008',
     'scene-1009', 'scene-1010', 'scene-1044', 'scene-1045', 'scene-1046', 'scene-1047', 'scene-1048', 'scene-1049',
     'scene-1050', 'scene-1051', 'scene-1052', 'scene-1053', 'scene-1054', 'scene-1055', 'scene-1056', 'scene-1057',
     'scene-1058', 'scene-1106', 'scene-1107', 'scene-1108', 'scene-1109', 'scene-1110']

train = list(sorted(set(train_detect + train_track)))

val = \
    ['carla-1005', 'carla-1010', 'carla-1015', 'carla-1020', 'carla-1025', 'carla-1030', 'carla-1035', 'carla-1040', 'carla-1045', 'carla-1050', 'carla-1055', 'carla-1060', 'carla-1065', 'carla-1070', 'carla-1075', 'carla-1080', 'carla-1085', 'carla-1090', 'carla-1095', 'carla-1100', 'carla-1105', 'carla-1110', 'carla-1115', 'carla-1120', 'carla-1125', 'carla-1130', 'carla-1135', 'carla-1140', 'carla-1145', 'carla-1150', 'carla-1155', 'carla-1160', 'carla-1165', 'carla-1170', 'carla-1175', 'carla-1180', 'carla-1185', 'carla-1190', 'carla-1195', 'carla-1200', 'carla-1205', 'carla-1210', 'carla-1215', 'carla-1220', 'carla-1225', 'carla-1230', 'carla-1235', 'carla-1240', 'carla-1245', 'carla-1250', 'carla-1255', 'carla-1260', 'carla-1265', 'carla-1270', 'carla-1275', 'carla-1280', 'carla-1285', 'carla-1290', 'carla-1295', 'carla-1300', 'carla-1305', 'carla-1310', 'carla-1315', 'carla-1320', 'carla-1325', 'carla-1330', 'carla-1335', 'carla-1340', 'carla-1345', 'carla-1350', 'carla-1355', 'carla-1360', 'carla-1365', 'carla-1370', 'carla-1375', 'carla-1380', 'carla-1385', 'carla-1390', 'carla-1395', 'carla-1400', 'carla-1405', 'carla-1410', 'carla-1415', 'carla-1420', 'carla-1425', 'carla-1430', 'carla-1435', 'carla-1440', 'carla-1445', 'carla-1450', 'carla-1455', 'carla-1460', 'carla-1465', 'carla-1470', 'carla-1475', 'carla-1480', 'carla-1485', 'carla-1490', 'carla-1495', 'carla-1500', 'carla-1505', 'carla-1510', 'carla-1515', 'carla-1520', 'carla-1525', 'carla-1530', 'carla-1535', 'carla-1540', 'carla-1545', 'carla-1550', 'carla-1555', 'carla-1560', 'carla-1565', 'carla-1570', 'carla-1575', 'carla-1580', 'carla-1585', 'carla-1590', 'carla-1595', 'carla-1600', 'carla-1605', 'carla-1610', 'carla-1615', 'carla-1620', 'carla-1625', 'carla-1630', 'carla-1635', 'carla-1640', 'carla-1645', 'carla-1650', 'carla-1655', 'carla-1660', 'carla-1665', 'carla-1670', 'carla-1675', 'carla-1680', 'carla-1685', 'carla-1690', 'carla-1695', 'carla-1700', 'carla-1705', 'carla-1710', 'carla-1715', 'carla-1720', 'carla-1725', 'carla-1730', 'carla-1735', 'carla-1740', 'carla-1745', 'carla-1750', 'carla-1755', 'carla-1760', 'carla-1765', 'carla-1770', 'carla-1775', 'carla-1780', 'carla-1785', 'carla-1790', 'carla-1795', 'carla-1800', 'carla-1805', 'carla-1810', 'carla-1815', 'carla-1820', 'carla-1825', 'carla-1830', 'carla-1835', 'carla-1840', 'carla-1845', 'carla-1850', 'carla-1855', 'carla-1860', 'carla-1865', 'carla-1870', 'carla-1875', 'carla-1880', 'carla-1885', 'carla-1890', 'carla-1895', 'carla-1900', 'carla-1905', 'carla-1910', 'carla-1915', 'carla-1920', 'carla-1925', 'carla-1930', 'carla-1935', 'carla-1940', 'carla-1945', 'carla-1950', 'carla-1955', 'carla-1960', 'carla-1965', 'carla-1970', 'carla-1975', 'carla-1980', 'carla-1985', 'carla-1990', 'carla-1995',
     'scene-0003', 'scene-0012', 'scene-0013', 'scene-0014', 'scene-0015', 'scene-0016', 'scene-0017', 'scene-0018',
     'scene-0035', 'scene-0036', 'scene-0038', 'scene-0039', 'scene-0092', 'scene-0093', 'scene-0094', 'scene-0095',
     'scene-0096', 'scene-0097', 'scene-0098', 'scene-0099', 'scene-0100', 'scene-0101', 'scene-0102', 'scene-0103',
     'scene-0104', 'scene-0105', 'scene-0106', 'scene-0107', 'scene-0108', 'scene-0109', 'scene-0110', 'scene-0221',
     'scene-0268', 'scene-0269', 'scene-0270', 'scene-0271', 'scene-0272', 'scene-0273', 'scene-0274', 'scene-0275',
     'scene-0276', 'scene-0277', 'scene-0278', 'scene-0329', 'scene-0330', 'scene-0331', 'scene-0332', 'scene-0344',
     'scene-0345', 'scene-0346', 'scene-0519', 'scene-0520', 'scene-0521', 'scene-0522', 'scene-0523', 'scene-0524',
     'scene-0552', 'scene-0553', 'scene-0554', 'scene-0555', 'scene-0556', 'scene-0557', 'scene-0558', 'scene-0559',
     'scene-0560', 'scene-0561', 'scene-0562', 'scene-0563', 'scene-0564', 'scene-0565', 'scene-0625', 'scene-0626',
     'scene-0627', 'scene-0629', 'scene-0630', 'scene-0632', 'scene-0633', 'scene-0634', 'scene-0635', 'scene-0636',
     'scene-0637', 'scene-0638', 'scene-0770', 'scene-0771', 'scene-0775', 'scene-0777', 'scene-0778', 'scene-0780',
     'scene-0781', 'scene-0782', 'scene-0783', 'scene-0784', 'scene-0794', 'scene-0795', 'scene-0796', 'scene-0797',
     'scene-0798', 'scene-0799', 'scene-0800', 'scene-0802', 'scene-0904', 'scene-0905', 'scene-0906', 'scene-0907',
     'scene-0908', 'scene-0909', 'scene-0910', 'scene-0911', 'scene-0912', 'scene-0913', 'scene-0914', 'scene-0915',
     'scene-0916', 'scene-0917', 'scene-0919', 'scene-0920', 'scene-0921', 'scene-0922', 'scene-0923', 'scene-0924',
     'scene-0925', 'scene-0926', 'scene-0927', 'scene-0928', 'scene-0929', 'scene-0930', 'scene-0931', 'scene-0962',
     'scene-0963', 'scene-0966', 'scene-0967', 'scene-0968', 'scene-0969', 'scene-0971', 'scene-0972', 'scene-1059',
     'scene-1060', 'scene-1061', 'scene-1062', 'scene-1063', 'scene-1064', 'scene-1065', 'scene-1066', 'scene-1067',
     'scene-1068', 'scene-1069', 'scene-1070', 'scene-1071', 'scene-1072', 'scene-1073']

test = \
    ['carla-7001', 'carla-7002', 'carla-7003', 'carla-7004', 'carla-7005', 'carla-7006', 'carla-7007', 'carla-7008', 'carla-7009', 'carla-7010', 'carla-7011', 'carla-7012', 'carla-7013', 'carla-7014', 'carla-7015', 'carla-7016', 'carla-7017', 'carla-7018', 'carla-7019', 'carla-7020', 'carla-7021', 'carla-7022', 'carla-7023', 'carla-7024', 'carla-7025', 'carla-7026', 'carla-7027', 'carla-7028', 'carla-7029', 'carla-7030', 'carla-7031', 'carla-7032', 'carla-7033', 'carla-7034', 'carla-7035', 'carla-7036', 'carla-7037', 'carla-7038', 'carla-7039', 'carla-7040', 'carla-7041', 'carla-7042', 'carla-7043', 'carla-7044', 'carla-7045', 'carla-7046', 'carla-7047', 'carla-7048', 'carla-7049', 'carla-7050', 'carla-7051', 'carla-7052', 'carla-7053', 'carla-7054', 'carla-7055', 'carla-7056', 'carla-7057', 'carla-7058', 'carla-7059', 'carla-7060', 'carla-7061', 'carla-7062', 'carla-7063', 'carla-7064', 'carla-7065', 'carla-7066', 'carla-7067', 'carla-7068', 'carla-7069', 'carla-7070', 'carla-7071', 'carla-7072', 'carla-7073', 'carla-7074', 'carla-7075', 'carla-7076', 'carla-7077', 'carla-7078', 'carla-7079', 'carla-7080', 'carla-7081', 'carla-7082', 'carla-7083', 'carla-7084', 'carla-7085', 'carla-7086', 'carla-7087', 'carla-7088', 'carla-7089', 'carla-7090', 'carla-7091', 'carla-7092', 'carla-7093', 'carla-7094', 'carla-7095', 'carla-7096', 'carla-7097', 'carla-7098', 'carla-7099', 'carla-7100', 'carla-7101', 'carla-7102', 'carla-7103', 'carla-7104', 'carla-7105', 'carla-7106', 'carla-7107', 'carla-7108', 'carla-7109', 'carla-7110', 'carla-7111', 'carla-7112', 'carla-7113', 'carla-7114', 'carla-7115', 'carla-7116', 'carla-7117', 'carla-7118', 'carla-7119',
     'scene-0077', 'scene-0078', 'scene-0079', 'scene-0080', 'scene-0081', 'scene-0082', 'scene-0083', 'scene-0084',
     'scene-0085', 'scene-0086', 'scene-0087', 'scene-0088', 'scene-0089', 'scene-0090', 'scene-0091', 'scene-0111',
     'scene-0112', 'scene-0113', 'scene-0114', 'scene-0115', 'scene-0116', 'scene-0117', 'scene-0118', 'scene-0119',
     'scene-0140', 'scene-0142', 'scene-0143', 'scene-0144', 'scene-0145', 'scene-0146', 'scene-0147', 'scene-0148',
     'scene-0265', 'scene-0266', 'scene-0279', 'scene-0280', 'scene-0281', 'scene-0282', 'scene-0307', 'scene-0308',
     'scene-0309', 'scene-0310', 'scene-0311', 'scene-0312', 'scene-0313', 'scene-0314', 'scene-0333', 'scene-0334',
     'scene-0335', 'scene-0336', 'scene-0337', 'scene-0338', 'scene-0339', 'scene-0340', 'scene-0341', 'scene-0342',
     'scene-0343', 'scene-0481', 'scene-0482', 'scene-0483', 'scene-0484', 'scene-0485', 'scene-0486', 'scene-0487',
     'scene-0488', 'scene-0489', 'scene-0490', 'scene-0491', 'scene-0492', 'scene-0493', 'scene-0494', 'scene-0495',
     'scene-0496', 'scene-0497', 'scene-0498', 'scene-0547', 'scene-0548', 'scene-0549', 'scene-0550', 'scene-0551',
     'scene-0601', 'scene-0602', 'scene-0603', 'scene-0604', 'scene-0606', 'scene-0607', 'scene-0608', 'scene-0609',
     'scene-0610', 'scene-0611', 'scene-0612', 'scene-0613', 'scene-0614', 'scene-0615', 'scene-0616', 'scene-0617',
     'scene-0618', 'scene-0619', 'scene-0620', 'scene-0621', 'scene-0622', 'scene-0623', 'scene-0624', 'scene-0827',
     'scene-0828', 'scene-0829', 'scene-0830', 'scene-0831', 'scene-0833', 'scene-0834', 'scene-0835', 'scene-0836',
     'scene-0837', 'scene-0838', 'scene-0839', 'scene-0840', 'scene-0841', 'scene-0842', 'scene-0844', 'scene-0845',
     'scene-0846', 'scene-0932', 'scene-0933', 'scene-0935', 'scene-0936', 'scene-0937', 'scene-0938', 'scene-0939',
     'scene-0940', 'scene-0941', 'scene-0942', 'scene-0943', 'scene-1026', 'scene-1027', 'scene-1028', 'scene-1029',
     'scene-1030', 'scene-1031', 'scene-1032', 'scene-1033', 'scene-1034', 'scene-1035', 'scene-1036', 'scene-1037',
     'scene-1038', 'scene-1039', 'scene-1040', 'scene-1041', 'scene-1042', 'scene-1043']

mini_train = \
    ['scene-0061', 'scene-0553', 'scene-0655', 'scene-0757', 'scene-0796', 'scene-1077', 'scene-1094', 'scene-1100']

mini_val = \
    ['scene-0103', 'scene-0916']


def create_splits_logs(split: str, nusc: 'NuScenes') -> List[str]:
    """
    Returns the logs in each dataset split of nuScenes.
    Note: Previously this script included the teaser dataset splits. Since new scenes from those logs were added and
          others removed in the full dataset, that code is incompatible and was removed.
    :param split: NuScenes split.
    :param nusc: NuScenes instance.
    :return: A list of logs in that split.
    """
    # Load splits on a scene-level.
    scene_splits = create_splits_scenes(verbose=False)

    assert split in scene_splits.keys(), 'Requested split {} which is not a known nuScenes split.'.format(split)

    # Check compatibility of split with nusc_version.
    version = nusc.version
    if split in {'train', 'val', 'train_detect', 'train_track'}:
        assert version.endswith('trainval'), \
            'Requested split {} which is not compatible with NuScenes version {}'.format(split, version)
    elif split in {'mini_train', 'mini_val'}:
        assert version.endswith('mini'), \
            'Requested split {} which is not compatible with NuScenes version {}'.format(split, version)
    elif split == 'test':
        assert version.endswith('test'), \
            'Requested split {} which is not compatible with NuScenes version {}'.format(split, version)
    else:
        raise ValueError('Requested split {} which this function cannot map to logs.'.format(split))

    # Get logs for this split.
    scene_to_log = {scene['name']: nusc.get('log', scene['log_token'])['logfile'] for scene in nusc.scene}
    logs = set()
    scenes = scene_splits[split]
    for scene in scenes:
        logs.add(scene_to_log[scene])

    return list(logs)


def create_splits_scenes(verbose: bool = False) -> Dict[str, List[str]]:
    """
    Similar to create_splits_logs, but returns a mapping from split to scene names, rather than log names.
    The splits are as follows:
    - train/val/test: The standard splits of the nuScenes dataset (700/150/150 scenes).
    - mini_train/mini_val: Train and val splits of the mini subset used for visualization and debugging (8/2 scenes).
    - train_detect/train_track: Two halves of the train split used for separating the training sets of detector and
        tracker if required.
    :param verbose: Whether to print out statistics on a scene level.
    :return: A mapping from split name to a list of scenes names in that split.
    """
    # Use hard-coded splits.
    all_scenes = train + val + test
    # assert len(all_scenes) == 1000 and len(set(all_scenes)) == 1000, 'Error: Splits incomplete!'
    scene_splits = {'train': train, 'val': val, 'test': test,
                    'mini_train': mini_train, 'mini_val': mini_val,
                    'train_detect': train_detect, 'train_track': train_track}

    # Optional: Print scene-level stats.
    if verbose:
        for split, scenes in scene_splits.items():
            print('%s: %d' % (split, len(scenes)))
            print('%s' % scenes)

    return scene_splits


if __name__ == '__main__':
    # Print the scene-level stats.
    create_splits_scenes(verbose=True)
