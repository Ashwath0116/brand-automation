# BizForge Database Report

## Tables
- **users** - 5 rows
- **sessions** - 6 rows
- **branding_logs** - 0 rows
- **activity_logs** - 2 rows

## Users

| ID | Name | Email | Provider | Admin | Created | Last Login |
|---|---|---|---|---|---|---|
| 1 | Test Admin | admin@test.com | local | No | 2026-02-13 17:05:32.280520 | 2026-02-13 17:05:52.348200 |
| 2 | KANTHA ASHWATH * | 23x51a3323@srecnandyal.edu.in | local | No | 2026-02-13 17:08:03.748340 | 2026-02-15 05:02:51.664406 |
| 3 | rahul | 23x51a3302@srecnandyal.edu.in | local | No | 2026-02-14 03:58:50.068362 | 2026-02-14 03:59:16.640059 |
| 4 | A K | rockashwath12@gmail.com | local | Yes | 2026-02-14 04:18:45.614701 | 2026-02-15 05:03:24.252285 |
| 5 | Ashwath Kantha | ashwathkantha220@gmail.com | google | No | 2026-02-14 06:33:53.831707 | 2026-02-14 06:33:53.831729 |

**Total users: 5**

## Active Sessions

**Total active sessions: 6**

- Session [1] User ID: 1 | Token: V7TQnkV-ZzoCYmz... | 2026-02-13 17:05:32.385229
- Session [3] User ID: 2 | Token: 3xqs5rcha1sbR39... | 2026-02-14 04:16:05.049014
- Session [4] User ID: 4 | Token: B6agrzlv1AGDahh... | 2026-02-14 04:18:45.641484
- Session [5] User ID: 2 | Token: xOMruN1njUK7yg0... | 2026-02-14 10:56:19.863545
- Session [6] User ID: 4 | Token: GqnCV32bfFeOHbI... | 2026-02-15 03:59:33.675741
- Session [7] User ID: 4 | Token: uGJRr3GEtQX5Q4m... | 2026-02-15 05:03:24.263133

## Activity Logs (Recent 20)

### Log #2
- **User:** rockashwath12@gmail.com
- **Action:** generate_brand
- **Status:** success
- **IP:** 127.0.0.1
- **Time:** 2026-02-15 05:07:44.872945
- **Input:**
```json
{"industry": "tech", "keywords": ["premium"], "tone": "Professional", "language": "te"}
```
- **Output:**
```json
{"brand_names": [{"name": "\u0c2a\u0c4d\u0c30\u0c40\u0c2e\u0c3f\u0c2f\u0c02\u0c1f\u0c46\u0c15\u0c4d", "explanation": "\u0c07\u0c26\u0c3f \u0c2a\u0c4d\u0c30\u0c40\u0c2e\u0c3f\u0c2f\u0c02 \u0c38\u0c4d\u0c25\u0c3e\u0c2f\u0c3f \u0c1f\u0c46\u0c15\u0c4d\u0c28\u0c3e\u0c32\u0c1c\u0c40\u0c28\u0c3f \u0c38\u0c42\u0c1a\u0c3f\u0c38\u0c4d\u0c24\u0c41\u0c02\u0c26\u0c3f."}, {"name": "\u0c1f\u0c46\u0c15\u0c4d\u0c28\u0c4b\u0c35\u0c47\u0c37\u0c28\u0c4d", "explanation": "\u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15 \u0c2a\u0c30\u0c3f\u0c1c\u0c4d\u0c1e\u0c3e\u0c28\u0c02 \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c28\u0c35\u0c40\u0c15\u0c30\u0c23\u0c15\u0c41 \u0c1a\u0c3f\u0c39\u0c4d\u0c28\u0c02."}, {"name": "\u0c2a\u0c4d\u0c30\u0c4a\u0c2b\u0c46\u0c37\u0c28\u0c32\u0c4d \u0c1f\u0c46\u0c15\u0c4d", "explanation": "\u0c35\u0c43\u0c24\u0c4d\u0c24\u0c3f\u0c2a\u0c30\u0c2e\u0c48\u0c28 \u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15 \u0c2a\u0c30\u0c3f\u0c37\u0c4d\u0c15\u0c3e\u0c30\u0c3e\u0c32\u0c15\u0c41 \u0c2a\u0c4d\u0c30\u0c24\u0c40\u0c15."}, {"name": "\u0c0e\u0c32\u0c48\u0c1f\u0c4d \u0c38\u0c3f\u0c38\u0c4d\u0c1f\u0c2e\u0c4d\u0c38\u0c4d", "explanation": "\u0c05\u0c24\u0c4d\u0c2f\u0c41\u0c28\u0c4d\u0c28\u0c24 \u0c38\u0c4d\u0c25\u0c3e\u0c2f\u0c3f \u0c38\u0c3f\u0c38\u0c4d\u0c1f\u0c2e\u0c4d\u0c38\u0c4d \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15\u0c24\u0c15\u0c41 \u0c1a\u0c3f\u0c39\u0c4d\u0c28\u0c02."}, {"name": "\u0c28\u0c46\u0c15\u0c4d\u0c38\u0c4d\u0c1f\u0c4d \u0c1c\u0c46\u0c28\u0c4d \u0c1f\u0c46\u0c15\u0c4d", "explanation": "\u0c24\u0c30\u0c41\u0c35\u0c3e\u0c24\u0c3f \u0c24\u0c30\u0c02 \u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15 \u0c2a\u0c30\u0c3f\u0c37\u0c4d\u0c15\u0c3e\u0c30\u0c3e\u0c32\u0c15\u0c41 \u0c2a\u0c4d\u0c30\u0c24\u0c40\u0c15."}, {"name": "\u0c1f\u0c46\u0c15\u0c4d\u0c28\u0c4b\u0c32\u0c3e\u0c1c\u0c40 \u0c39\u0c2c\u0c4d", "explanation": "\u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15 \u0c2a\u0c30\u0c3f\u0c1c\u0c4d\u0c1e\u0c3e\u0c28\u0c02 \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c05\u0c2d\u0c3f\u0c35\u0c43\u0c26\u0c4d\u0c27\u0c3f\u0c15\u0c3f \u0c15\u0c47\u0c02\u0c26\u0c4d\u0c30\u0c02."}, {"name": "\u0c07\u0c28\u0c4d\u0c28\u0c4b\u0c35\u0c47\u0c37\u0c28\u0c4d \u0c1f\u0c46\u0c15\u0c4d", "explanation": "\u0c28\u0c35\u0c40\u0c15\u0c30\u0c23 \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15 \u0c2a\u0c30\u0c3f\u0c1c\u0c4d\u0c1e\u0c3e\u0c28\u0c3e\u0c28\u0c3f\u0c15\u0c3f \u0c1a\u0c3f\u0c39\u0c4d\u0c28\u0c02."}, {"name": "\u0c2a\u0c4d\u0c30\u0c40\u0c2e\u0c3f\u0c2f\u0c02 \u0c38\u0c3f\u0c38\u0c4d\u0c1f\u0c2e\u0c4d\u0c38\u0c4d", "explanation": "\u0c2a\u0c4d\u0c30\u0c40\u0c2e\u0c3f\u0c2f\u0c02 \u0c38\u0c4d\u0c25\u0c3e\u0c2f\u0c3f \u0c38\u0c3f\u0c38\u0c4d\u0c1f\u0c2e\u0c4d\u0c38\u0c4d \u0c2e\u0c30\u0c3f\u0c2f\u0c41 \u0c38\u0c3e\u0c02\u0c15\u0c47\u0c24\u0c3f\u0c15\u0c24\u0c15\u0c41 \u0c2a\u0c4d\u0c30\u0c24\u0c40\u0c15."}]}
```

### Log #1
- **User:** 23x51a3323@srecnandyal.edu.in
- **Action:** generate_brand
- **Status:** success
- **IP:** 127.0.0.1
- **Time:** 2026-02-15 05:03:05.882757
- **Input:**
```json
{"industry": "tech", "keywords": ["fast"], "tone": "Professional", "language": "te"}
```
- **Output:**
```json
{"count": 11}
```


**Total activity logs: 2**
