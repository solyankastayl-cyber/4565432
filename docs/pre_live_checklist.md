# Pre-Live Readiness Checklist

**Version:** 1.0  
**Last Updated:** 2026-03-15

---

## 1) Data Integrity
- [ ] Источники market data стабильны (нет пропусков/скачков)
- [ ] Timestamp синхронизирован (NTP / exchange time drift < 100 ms)
- [ ] Проверки на NaN / отрицательные цены / нулевой объём
- [ ] Orderbook snapshots валидны (spread > 0, depth ≥ минимального)

## 2) Technical Analysis / Research Logic
- [ ] Нет lookahead bias во всех индикаторах
- [ ] Одинаковые входные данные → детерминированный результат
- [ ] Fractal similarity возвращает значения только в диапазоне [0, 1]
- [ ] Capital flow / regime / reflexivity не дублируют сигналы (no double counting)
- [ ] Все modifiers ограничены диапазоном (например 0.85–1.15)

## 3) Coefficient / Weight Audit
- [ ] Во всех формулах сумма весов = 1
- [ ] Ни один слой не доминирует > 40% итогового score
- [ ] Sensitivity analysis (±20%) не ломает ranking сигналов
- [ ] Meta-Alpha weights корректно нормализуются

## 4) Signal Lifecycle
- [ ] Alpha Decay корректно переводит сигналы в EXPIRED
- [ ] TTL сигналов соответствует half-life стратегии
- [ ] Execution блокируется для EXPIRED signals

## 5) Portfolio & Risk
- [ ] Portfolio exposure ≤ заданных лимитов
- [ ] Risk budget не превышает global portfolio risk cap
- [ ] VaR / drawdown рассчитываются без NaN и overflow
- [ ] Correlation matrix корректна (симметричная, диагональ = 1)

## 6) Execution Logic
- [ ] Order routing выбирает правильную биржу
- [ ] MARKET / LIMIT / TWAP выбор соответствует liquidity state
- [ ] Slippage estimation не отрицательное и не нереалистично маленькое
- [ ] Execution Brain блокирует сделки при extreme risk

## 7) Exchange Integration
- [ ] API keys работают (read / trade permissions)
- [ ] Position sync совпадает с биржей
- [ ] Partial fills корректно обрабатываются
- [ ] Duplicate orders не создаются

## 8) Reconciliation
- [ ] Exchange state = internal portfolio state
- [ ] Балансы совпадают с биржей
- [ ] Missing fills автоматически восстанавливаются

## 9) Safety Layer
- [ ] Circuit Breaker срабатывает при drawdown / slippage spike
- [ ] Kill Switch мгновенно блокирует новые ордера
- [ ] Trade Throttle ограничивает burst-execution

## 10) Stress / Chaos Testing
- [ ] Signal storm (≥500 signals/min) проходит без crash
- [ ] Execution burst (≥50 orders/10 s) стабилен
- [ ] Exchange disconnect корректно обрабатывается
- [ ] Latency spike не ломает pipeline
- [ ] Portfolio shock (-15%) не приводит к overflow ошибок

## 11) Metrics / Telemetry
- [ ] Latency (avg / p95 / p99) логируется
- [ ] Execution throughput отслеживается
- [ ] Error rate < заданного threshold
- [ ] Health endpoint возвращает корректный статус

## 12) Validation Dashboard
- [ ] system_validation.run проходит без CRITICAL ошибок
- [ ] system_score ≥ 90
- [ ] Все integration chains проходят тесты

---

## Критерии готовности к Stage C

| Metric | Threshold |
|--------|-----------|
| Validation Score | ≥ 90 |
| Stress Tests | PASS |
| Chaos Tests | PASS |
| Error Rate | < 0.5% |
| Latency p99 | < 250 ms |
| Sharpe (pilot) | > 1.5 |
| Successful Trades | ≥ 50 |

---

## Stages

| Stage | Mode | Capital | Requirements |
|-------|------|---------|--------------|
| A | PAPER | 0 | Basic tests pass |
| B | APPROVAL | $1k | Validation ≥ 80 |
| C | PILOT | $10k | Validation ≥ 90, 50+ trades |
| D | LIVE | Full | Stage C criteria + 30 days stable |
