import pandas as pd

def verify_results():
    try:
        df = pd.read_csv('outputs/output.csv')
    except FileNotFoundError:
        print("Error: outputs/output.csv not found. Run pipeline first.")
        return

    print("=== Running Verification Checks ===\n")
    tests_passed = 0
    total_tests = 4

    # Test 1: Delhi-Jaipur (2024-11-11)
    print("Test 1: Delhi-Jaipur Sample Row Check")
    dj = df[(df['route'] == 'Delhi-Jaipur') & (df['week_of'] == '2024-11-11')]
    if not dj.empty and dj.iloc[0]['flagged'] == 'Yes' and "+35.5%" in dj.iloc[0]['vs_own_history'] and "+21.0%" in dj.iloc[0]['vs_similar_routes']:
        print("✅ PASSED: Delhi-Jaipur matched exactly.")
        tests_passed += 1
    else:
        print("❌ FAILED: Delhi-Jaipur did not match.")

    # Test 2: Ahmedabad-Mumbai (2025-01-20)
    print("\nTest 2: Ahmedabad-Mumbai Sample Row Check")
    am = df[(df['route'] == 'Ahmedabad-Mumbai') & (df['week_of'] == '2025-01-20')]
    if not am.empty and am.iloc[0]['flagged'] == 'No (justified)' and am.iloc[0]['matched_note_id'] == 'N002':
        print("✅ PASSED: Ahmedabad-Mumbai matched exactly and was justified by N002.")
        tests_passed += 1
    else:
        print("❌ FAILED: Ahmedabad-Mumbai did not match.")

    # Test 3: Chennai-Bangalore Trap (Flood Window)
    print("\nTest 3: Chennai-Bangalore Flood Window Trap")
    cb_justified = df[(df['route'] == 'Chennai-Bangalore') & (df['week_of'].isin(['2025-02-24', '2025-03-03']))]
    cb_unexplained = df[(df['route'] == 'Chennai-Bangalore') & (df['week_of'].isin(['2025-03-10', '2025-03-17']))]
    
    if len(cb_justified) == 2 and all(cb_justified['flagged'] == 'No (justified)') and \
       len(cb_unexplained) == 2 and all(cb_unexplained['flagged'] == 'Yes'):
        print("✅ PASSED: Successfully justified flood weeks and caught unexplained trap weeks.")
        tests_passed += 1
    else:
        print("❌ FAILED: Chennai-Bangalore trap failed.")

    # Test 4: Mumbai-Pune Slow Creep
    print("\nTest 4: Mumbai-Pune Slow Creep Detection")
    mp = df[(df['route'] == 'Mumbai-Pune')]
    if len(mp) > 5 and all(mp['flagged'] == 'Yes'):
        print("✅ PASSED: Successfully detected long-term slow creep despite low vs_own_history percentages.")
        tests_passed += 1
    else:
        print("❌ FAILED: Mumbai-Pune drift was not properly detected.")

    print(f"\n=== Final Score: {tests_passed}/{total_tests} Tests Passed ===")
    if tests_passed == total_tests:
        print("🎉 Everything is working perfectly! You are ready to submit.")

if __name__ == "__main__":
    verify_results()
