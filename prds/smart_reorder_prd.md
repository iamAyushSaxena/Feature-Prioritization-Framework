# Product Requirement Document: Smart Reorder

## 1. Overview

**Feature Name**: Smart Reorder  
**Product**: *Hungry Panda*
**Author**: *Ayush Saxena*  
**Date**: December 2025  
**Status**: Proposed  
**Priority**: P0 (Highest)

---

## 2. Problem Statement

**Current State**: Users spend an average of 8-12 minutes browsing restaurants and items each time they order. Analysis shows that 65% of users repeatedly order from the same 3-5 restaurants, yet they navigate through the entire app flow every time.

**Pain Points**:
- Cognitive load of re-making the same decision
- Time wasted browsing familiar menus
- Friction in checkout flow reduces conversion
- Users forget their previous favorite orders

**User Quotes**:
> "I order the same thing from the same restaurant every week, but I still have to search for it every time." - User Interview #12

> "I wish there was a 'reorder last meal' button." - App Store Review

---

## 3. Goals & Success Metrics

### Primary Goal
Increase repeat order frequency by reducing friction in the reorder journey.

### Success Metrics
| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Repeat Order Rate | 40% | 48% (+20%) | Orders from same restaurant within 30 days |
| Time to Checkout | 8.5 min | 4.5 min (-47%) | Median time from app open to order placed |
| D7 Retention | 45% | 50% (+11%) | % of new users active after 7 days |
| Orders per User/Month | 2.5 | 2.9 (+16%) | Average monthly order frequency |

### Secondary Metrics
- Click-through rate on Smart Reorder suggestions
- Revenue per user (RPU)
- Customer satisfaction score (CSAT)

### Guardrail Metrics
- Restaurant discovery rate (should not decrease)
- Average order value (should not decrease)
- New restaurant trial rate (maintain >20%)

---

## 4. Target Users

### Primary Persona: "The Routine Orderer"
- **Demographics**: 25-40 years old, working professionals
- **Behavior**: Orders 2-4 times per week, 70%+ orders from same restaurants
- **Motivation**: Convenience, time-saving, consistency
- **Tech-savviness**: High

### Secondary Persona: "The Busy Parent"
- **Demographics**: 30-45 years old, families with children
- **Behavior**: Orders family meals 1-2 times per week
- **Motivation**: Feeding family quickly, minimal decision-making
- **Tech-savviness**: Medium

---

## 5. Solution: Smart Reorder Feature

### 5.1 Core Functionality

**One-Tap Reorder**:
- Surface user's last 3 orders prominently on homepage
- Single tap to add entire previous order to cart
- Show expected delivery time and total cost upfront

**Smart Suggestions**:
- ML-powered recommendations based on:
  - Order history (frequency, recency)
  - Time of day patterns (breakfast vs dinner orders)
  - Day of week patterns (weekend vs weekday)
  - Contextual signals (weather, holidays)

**Customization Options**:
- Edit reorder before checkout (add/remove items)
- Set favorite orders for ultra-quick access
- Schedule recurring orders (optional)

### 5.2 User Flow
```
[App Open] → [Homepage with Reorder Cards] → [Tap Smart Reorder]
    ↓
[Review Cart (pre-filled)] → [Confirm Address] → [Confirm Payment]
    ↓
[Order Placed] → [Tracking Screen]
```

**Alternate Flow (Editing)**:
```
[Tap Smart Reorder] → [Tap "Edit Order"] → [Add/Remove Items]
    ↓
[Review Cart] → [Checkout] → [Order Placed]
```

### 5.3 UI/UX Mockups

**Homepage Placement**:
- Horizontal scrollable cards below search bar
- Each card shows: Restaurant name, items, total price, delivery time
- Visual: Restaurant logo + food photos

**Card Design**:
```
┌────────────────────────────────────────┐
│  [Restaurant Logo]                     │
│  Restaurant Name                       │
│  Item 1, Item 2, +3 more               │
│                                        │
│  ₹350 • 30 min delivery                │
│                                        │
│  [Reorder Now Button]                  │
└────────────────────────────────────────┘
```

---

## 6. User Stories & Acceptance Criteria

### Epic 1: Display Smart Reorder Cards

**User Story 1.1**: Display Recent Orders  
**As a** returning user  
**I want to** see my recent orders on the homepage  
**So that** I can quickly reorder without searching

**Acceptance Criteria**:
- [ ] Display last 3 unique orders (different restaurants)
- [ ] Show order within 30 days only
- [ ] Display restaurant name, items (max 3 visible), price, ETA
- [ ] Cards are horizontally scrollable
- [ ] Load time < 500ms

**User Story 1.2**: One-Tap Reorder  
**As a** busy user  
**I want to** reorder with one tap  
**So that** I can checkout faster

**Acceptance Criteria**:
- [ ] Tapping card opens review screen with pre-filled cart
- [ ] All previous items added to cart automatically
- [ ] Address and payment pre-selected from previous order
- [ ] Show "Edit Order" option clearly
- [ ] Confirm order within 2 taps from homepage

### Epic 2: Smart Suggestions Algorithm

**User Story 2.1**: Personalized Suggestions  
**As a** frequent user  
**I want** suggestions based on my patterns  
**So that** recommendations feel relevant

**Acceptance Criteria**:
- [ ] Algorithm considers order frequency (weight: 40%)
- [ ] Algorithm considers recency (weight: 30%)
- [ ] Algorithm considers time/day context (weight: 20%)
- [ ] Algorithm considers successful orders only (weight: 10%)
- [ ] Minimum 3 previous orders to show suggestions
- [ ] Suggestions refresh daily

**User Story 2.2**: Cold Start Handling  
**As a** new user  
**I want** to not see empty reorder section  
**So that** my experience isn't broken

**Acceptance Criteria**:
- [ ] Hide Smart Reorder section for users with <2 orders
- [ ] Show "Popular in Your Area" instead
- [ ] Transition to Smart Reorder after 2nd order

---

## 7. Technical Requirements

### 7.1 Backend
- **API Endpoint**: `GET /api/v1/users/{user_id}/smart-reorder`
- **Response**: JSON array of suggested orders with metadata
- **Caching**: Redis cache for 24 hours
- **Database**: Add `user_order_history` table with indexes on user_id, restaurant_id, order_date

### 7.2 ML Model
- **Algorithm**: Collaborative filtering + time-series analysis
- **Features**:
  - User order frequency vector
  - Restaurant affinity scores
  - Temporal patterns (hour, day, week)
  - Contextual features (weather, holidays)
- **Training Data**: Last 90 days of order history
- **Retraining**: Weekly batch job
- **Performance**: <100ms inference time

### 7.3 Frontend
- **Framework**: React Native
- **State Management**: Redux
- **Caching**: Local storage for last-fetched suggestions
- **Offline Support**: Show cached suggestions if network unavailable

### 7.4 Analytics
- **Events to Track**:
  - `smart_reorder_viewed`
  - `smart_reorder_tapped`
  - `smart_reorder_confirmed`
  - `smart_reorder_edited`
  - `smart_reorder_abandoned`
- **Properties**: user_id, restaurant_id, order_value, items_count

---

## 8. Dependencies & Risks

### Dependencies
- ML infrastructure for model training/serving
- Order history data pipeline (assume already exists)
- Restaurant menu API for item availability checks

### Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Restaurant menu items unavailable | High | Medium | Check item availability real-time; suggest substitutes |
| Poor ML recommendations | Medium | Low | Fallback to simple recency-based sorting |
| Performance degradation | High | Low | Implement aggressive caching; load asynchronously |
| Cannibalization of discovery | Medium | Medium | Monitor discovery metrics; balance with exploration features |

---

## 9. Implementation Plan

### Phase 1: MVP (Sprint 1-2, 4 weeks)
- Display last 3 orders (no ML)
- One-tap reorder functionality
- Basic edit capability
- Analytics instrumentation

### Phase 2: Smart Suggestions (Sprint 3-4, 4 weeks)
- ML model development
- Personalized recommendations
- A/B test framework
- Cold start handling

### Phase 3: Polish & Scale (Sprint 5-6, 4 weeks)
- Performance optimization
- Advanced editing features
- Schedule recurring orders
- Full rollout (100% of users)

**Total Timeline**: 12 weeks (3 months)  
**Team Size**: 2 engineers, 1 ML engineer, 1 designer, 1 PM

---

## 10. Go-to-Market Strategy

### Launch Plan
1. **Internal Beta** (Week 1-2): Test with employee users
2. **Closed Beta** (Week 3-4): 5% of power users (>10 orders/month)
3. **A/B Test** (Week 5-6): 50% rollout, measure impact
4. **Full Launch** (Week 7): 100% rollout with marketing push

### Marketing
- In-app notifications: "Introducing Smart Reorder!"
- Email campaign to frequent users
- Social media announcement
- Press release (if metrics exceed targets)

### Success Criteria for Launch Decision
- A/B test shows >5% lift in repeat orders (p<0.05)
- No negative impact on discovery metrics
- <0.1% crash rate
- >60% of eligible users engage with feature

---

## 11. Open Questions
- [ ] Should we allow reordering from restaurants currently closed?
- [ ] How to handle price changes since last order?
- [ ] Should we notify users of new items at their favorite restaurants?
- [ ] What's the right balance between familiarity and discovery?

---

## 12. Appendix

### A. Competitive Analysis
- **Swiggy**: Has "Reorder" button in order history (buried)
- **Zomato**: No prominent reorder feature
- **DoorDash**: "Reorder" in past orders section
- **Uber Eats**: "Order Again" carousel on homepage (good UX)

**Differentiation**: Our ML-powered suggestions + one-tap checkout creates superior experience.

### B. User Research Summary
- Conducted 22 user interviews (Nov 2025)
- 18/22 users expressed desire for easier reordering
- Average perceived time savings: 5-7 minutes
- Willingness to use: 9/10 (avg)

---

**Document History**:
- v1.0 (Dec 2025): Initial draft
- v1.1 (TBD): Post stakeholder review
