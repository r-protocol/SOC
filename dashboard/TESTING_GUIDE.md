# Dashboard Enhancements - Testing Guide

## Quick Start Testing

### Prerequisites
1. Ensure the backend API is running: `python dashboard/backend/app.py`
2. Ensure the frontend is running: `cd dashboard/frontend && npm run dev`
3. Have some articles in your database (run `python main.py` if needed)

---

## Test 1: Source Intelligence Coverage (Top 10 Feeds)

**What to Test:**
- Navigate to the dashboard
- Scroll to the "Source Intelligence Coverage" section
- Verify it shows actual sources from your database

**Expected Results:**
- Should display up to 10 sources (feeds)
- Sources should be sorted by article count (highest first)
- Names should be readable (e.g., "BleepingComputer", not "bleepingcomputer.com")
- Article counts should match your database

**Success Criteria:**
✅ Shows real sources from your database
✅ Top source has the highest article count
✅ Display names are clean and readable

---

## Test 2: Time Range Filter for Recent Threats

**What to Test:**
1. At the top of the dashboard, use the time range filter
2. Try different options: 1 day, 3 days, 7 days, 15 days, 30 days
3. Try custom days option (e.g., enter 45)
4. Try date range option (select start and end dates)
5. Observe the Recent Threats section updates

**Expected Results:**
- Recent Threats should update immediately when time range changes
- The blue info text should show current time range
- Only articles from the selected time period should appear
- Other dashboard sections should also update

**Success Criteria:**
✅ Recent Threats updates when time range changes
✅ Article dates match the selected time range
✅ No errors in browser console

---

## Test 3: IOC and KQL Counts Display

**What to Test:**
1. Look at the Recent Threats section
2. Each threat card should show metadata at the bottom
3. Check for IOC and KQL counts

**Expected Results:**
- Each card shows: `📅 Date • 🎯 X IOCs • 📊 Y KQL`
- Articles with analysis should have non-zero counts
- Unanalyzed articles should show `0 IOCs • 0 KQL`

**Success Criteria:**
✅ Both IOC and KQL counts are visible
✅ Counts are accurate (verify against database if needed)
✅ Icons display correctly

---

## Test 4: Clickable Articles with Modal

### Test 4A: Click Interaction
**What to Test:**
1. Click on any threat card in Recent Threats
2. Modal should open
3. Modal should show loading state briefly
4. Full article details should appear

**Expected Results:**
- Cursor changes to pointer on hover
- Modal opens on click
- Loading indicator appears briefly
- Modal content loads successfully

**Success Criteria:**
✅ Cards are clickable
✅ Modal opens smoothly
✅ No JavaScript errors

### Test 4B: Analyzed Article Modal
**What to Test:**
1. Click on a threat card that has been fully analyzed
2. Verify all sections are present

**Expected Results:**
Modal should show:
- ✅ Title at the top with close button
- ✅ Metadata grid (Risk Level, Category, Published Date, IOC/KQL counts)
- ✅ Source URL (clickable link)
- ✅ Summary section (with actual content)
- ✅ Recommendations section (bullet list if available)
- ✅ IOCs section with full list
  - Each IOC shows type, value, and context
  - Color-coded by type
  - Scrollable if many IOCs
- ✅ KQL Queries section with full queries
  - Query name and metadata
  - Formatted query text in code block
  - Scrollable if long

**Success Criteria:**
✅ All sections render correctly
✅ Data is accurate
✅ Formatting is readable
✅ Colors and styling are consistent

### Test 4C: Unanalyzed Article Modal
**What to Test:**
1. Click on a threat card with `0 IOCs • 0 KQL`
2. Check for warning indicators

**Expected Results:**
- Summary shows "Not analyzed - fetched only" or similar
- IOCs section shows "No IOCs extracted (article may not be fully analyzed)"
- KQL section shows "No KQL queries generated (article may not be fully analyzed)"
- Yellow warning banner at bottom explaining the article isn't analyzed

**Success Criteria:**
✅ Clear indicators for missing data
✅ No JavaScript errors
✅ Warning banner is visible and informative

### Test 4D: Modal Interactions
**What to Test:**
1. Open modal
2. Try scrolling within the modal
3. Click the close button
4. Click outside the modal (on the dark background)
5. Open modal, close it, open another article

**Expected Results:**
- Modal content scrolls independently
- Close button closes the modal
- Clicking outside closes the modal
- Can open different articles sequentially

**Success Criteria:**
✅ Scrolling works smoothly
✅ Both close methods work
✅ No memory leaks or performance issues

---

## Edge Cases to Test

### Edge Case 1: Empty Database
- **Test:** View dashboard with no articles
- **Expected:** Graceful "No data" messages, no errors

### Edge Case 2: Article with Many IOCs
- **Test:** Click article with 50+ IOCs
- **Expected:** IOCs section is scrollable, all IOCs visible

### Edge Case 3: Long KQL Queries
- **Test:** Click article with very long KQL queries
- **Expected:** Queries are formatted, scrollable, readable

### Edge Case 4: Missing Fields
- **Test:** Article with null/missing summary or recommendations
- **Expected:** Sections don't break, show "N/A" or skip gracefully

### Edge Case 5: Special Characters
- **Test:** Article with special characters in title, summary, IOCs
- **Expected:** Characters render correctly, no encoding issues

---

## Browser Compatibility

Test on:
- ✅ Chrome/Edge (Chromium)
- ✅ Firefox
- ✅ Safari (if on Mac)

---

## Performance Testing

1. **Load Time:** Dashboard should load within 2-3 seconds
2. **Filter Response:** Time range changes should update in <1 second
3. **Modal Open:** Should open instantly (<500ms)
4. **Scrolling:** Should be smooth with many articles

---

## Common Issues & Solutions

### Issue: "No threats found"
**Solution:** Check time range filter - you might be filtering to a period with no articles

### Issue: Modal shows loading forever
**Solution:** Check backend is running and console for API errors

### Issue: RSS Feed Stats shows "0" articles
**Solution:** Verify your database has articles with URLs populated

### Issue: KQL counts always show 0
**Solution:** Run pipeline with `--kql` flag to generate KQL queries: `python main.py --kql`

### Issue: Modal doesn't close
**Solution:** Check browser console for JavaScript errors, refresh page

---

## Reporting Issues

If you find bugs, note:
1. What you were doing
2. What you expected
3. What actually happened
4. Browser console errors
5. Browser and version

---

## Success Checklist

After testing, verify:
- ✅ RSS Feed Stats shows top 10 actual sources
- ✅ Time range filter affects Recent Threats
- ✅ Both IOC and KQL counts visible on threat cards
- ✅ All threat cards are clickable
- ✅ Modal displays complete article details
- ✅ Modal handles analyzed and unanalyzed articles correctly
- ✅ No console errors during normal usage
- ✅ Performance is acceptable

---

## Next Steps

Once testing is complete:
1. Use the dashboard for actual threat intelligence work
2. Provide feedback on usability
3. Identify any additional features you'd like
4. Report any bugs or issues found

Happy Testing! 🚀
