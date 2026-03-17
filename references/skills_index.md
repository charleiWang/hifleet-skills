# 技能清单 / Skills Index

中英双语。

---

## 1. 船位 / Ship Position ✅

| 中文 | 英文 |
|------|------|
| 名称 | 船位 / Ship Position |
| 描述 | 查询船舶实时或历史位置，支持 AIS 报位、锚位、靠泊等。 |
| 触发词 | 船位、位置、报位、在哪、轨迹、AIS 位置 / ship position, vessel position, location, AIS position, track, where is |

## 2. 档案 / Archive ✅

| 中文 | 英文 |
|------|------|
| 名称 | 档案 / Archive (Vessel Profile) |
| 描述 | 船舶与公司档案：船籍、船型、建造年份、船东、管理公司等。按 IMO 查询。 |
| 触发词 | 档案、船舶信息、船籍、船型、船东、管理公司 / archive, vessel profile, ship info, flag, ship type, owner, manager |

## 3. 红海/波斯湾海峡通航 / Strait Traffic ✅

| 中文 | 英文 |
|------|------|
| 名称 | 红海/波斯湾海峡通航 / Strait Traffic |
| 描述 | 咽喉航道通航船舶统计：曼德、苏伊士、好望角、霍尔木兹；POST 接口；无 token 限最近 1 周，有 token 时间不限。 |
| 触发词 | 红海、波斯湾、海峡通航、曼德、苏伊士、好望角、霍尔木兹 / Red Sea, Persian Gulf, strait traffic, Suez, Cape of Good Hope, Hormuz |

## 4. 区域船舶 / Area Traffic ✅

| 中文 | 英文 |
|------|------|
| 名称 | 区域船舶 / Area Traffic |
| 描述 | 查询指定矩形区域内的当前船舶列表，需 token；支持 bbox（左下/右上经纬度）。 |
| 触发词 | 区域船舶、范围内船舶、区域船位、某区域有多少船 / area traffic, vessels in area, ships in region |

## 5. 港口 / Port

| 中文 | 英文 |
|------|------|
| 名称 | 港口 / Port |
| 描述 | 港口列表、泊位、锚地、靠离泊计划与港口动态。 |
| 触发词 | 港口、泊位、锚地、靠港、离港、港口信息 / port, berth, anchorage, port call, arrival, departure, port info |

## 6. 性能 / Performance

| 中文 | 英文 |
|------|------|
| 名称 | 性能 / Performance |
| 描述 | 航速、油耗、主机负荷、能效（EEOI）及性能报告。 |
| 触发词 | 性能、油耗、航速、主机、能效、EEOI / performance, fuel consumption, speed, main engine, EEOI, efficiency |

## 7. 航程 / Voyage

| 中文 | 英文 |
|------|------|
| 名称 | 航程 / Voyage |
| 描述 | 航次、航程段、挂港顺序、ETA/ETD、航程统计。 |
| 触发词 | 航程、航次、挂港、ETA、ETD、航程段 / voyage, voyage leg, port call, ETA, ETD, voyage segment |

## 8. 航线 / Route

| 中文 | 英文 |
|------|------|
| 名称 | 航线 / Route |
| 描述 | 推荐航线、航路点、距离与航时、历史航线对比。 |
| 触发词 | 航线、航路、推荐航线、距离、航时、航路点 / route, shipping route, recommended route, distance, sailing time, waypoint |

## 9. 租船 / Charter

| 中文 | 英文 |
|------|------|
| 名称 | 租船 / Charter |
| 描述 | 租约、租家、租金、租期、合同条款及租船市场。 |
| 触发词 | 租船、租约、租家、租金、租期、合同 / charter, charter party, charterer, hire, period, contract |

## 10. 航运 / Shipping

| 中文 | 英文 |
|------|------|
| 名称 | 航运 / Shipping |
| 描述 | 运价、运力、市场动态、船舶买卖、航运新闻与行业数据。 |
| 触发词 | 航运、运价、运力、市场、买卖、航运新闻 / shipping, freight rate, tonnage, market, sale and purchase, shipping news |

## 11. 气象海况 / Weather & Sea Conditions

| 中文 | 英文 |
|------|------|
| 名称 | 气象海况 / Weather & Sea Conditions |
| 描述 | 风、浪、涌、能见度、台风/气旋路径及航行气象建议。 |
| 触发词 | 气象、海况、风、浪、台风、能见度 / weather, sea conditions, wind, wave, typhoon, visibility |

## 12. 船队 / Fleet

| 中文 | 英文 |
|------|------|
| 名称 | 船队 / Fleet |
| 描述 | 多船监控、船队分布、统计、报警汇总及船队报表。 |
| 触发词 | 船队、多船、船队分布、船队统计、船队报表 / fleet, multi-vessel, fleet distribution, fleet statistics, fleet report |

## 13. AIS

| 中文 | 英文 |
|------|------|
| 名称 | AIS |
| 描述 | AIS 报文、船舶识别、动态/静态数据、轨迹回放与导出。 |
| 触发词 | AIS、报文、MMSI、轨迹回放、AIS 数据 / AIS, message, MMSI, track replay, AIS data |

---

建议实现顺序：船位 → AIS → 档案 → 港口 → 航程 → 航线 → 性能 → 气象海况 → 船队 → 租船 → 航运。
