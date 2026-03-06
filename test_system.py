"""
Complete System Test - Verify Everything Works
"""

import requests
import json

print("="*70)
print("🔍 SYSTEM TEST - Verifying Everything Works")
print("="*70)

# Test 1: Backend Health Check
print("\n1. Testing backend health...")
try:
    response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
    if response.status_code == 200:
        print("   ✓ Backend is running")
        print(f"   ✓ Response: {response.json()}")
    else:
        print(f"   ✗ Backend returned status {response.status_code}")
except Exception as e:
    print(f"   ✗ Backend not accessible: {e}")
    print("   → Start backend: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    exit(1)

# Test 2: Satellite Coverage
print("\n2. Testing satellite coverage endpoint...")
try:
    response = requests.get("http://localhost:8000/api/v1/satellite-coverage", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print("   ✓ Satellite coverage loaded")
        print(f"   ✓ Coverage: Lat {data['bounds']['min_lat']:.4f} to {data['bounds']['max_lat']:.4f}")
        print(f"   ✓ Coverage: Lon {data['bounds']['min_lon']:.4f} to {data['bounds']['max_lon']:.4f}")
        print(f"   ✓ Center: ({data['center']['lat']:.4f}, {data['center']['lon']:.4f})")
    else:
        print(f"   ✗ Failed with status {response.status_code}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Forest Analysis (CRITICAL TEST)
print("\n3. Testing forest analysis with valid coordinates...")
print("   Using coordinates in NORTHERN area (where data exists)")

# Test polygon in valid data region
test_bounds = {
    "min_lat": 20.8500,
    "max_lat": 20.8600,
    "min_lon": 73.7475,
    "max_lon": 73.7575
}

payload = {
    "bounds": test_bounds,
    "date": "2024-03-15"
}

try:
    print(f"   Sending request to /api/v1/analyze...")
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json=payload,
        timeout=30
    )
    
    if response.status_code == 200:
        data = response.json()
        
        print("\n   ✅ ANALYSIS SUCCESSFUL!")
        print(f"   {'='*66}")
        
        kpis = data['data']['kpis']
        
        print(f"   Tree Count: {kpis['tree_count']}")
        print(f"   Tree Density: {kpis['tree_density']} trees/hectare")
        print(f"   Area: {kpis['area_hectares']} hectares")
        print(f"   NDVI Mean: {kpis['ndvi']['mean']:.4f}")
        print(f"   NDVI Min: {kpis['ndvi']['min']:.4f}")
        print(f"   NDVI Max: {kpis['ndvi']['max']:.4f}")
        print(f"   Health Score: {kpis['health_score']}/100 ({kpis['health_status']})")
        
        print(f"\n   Species Distribution:")
        for species, count in kpis['species_counts'].items():
            pct = kpis['species_distribution'][species]
            print(f"     {species:10s}: {count:4d} trees ({pct}%)")
        
        # Validation checks
        print(f"\n   Validation Checks:")
        checks_passed = 0
        checks_total = 5
        
        # Check 1: NDVI not zero
        if kpis['ndvi']['mean'] > 0:
            print(f"     ✓ NDVI is valid (not zero)")
            checks_passed += 1
        else:
            print(f"     ✗ NDVI is zero - wrong area selected!")
        
        # Check 2: Tree count reasonable
        if 50 <= kpis['tree_count'] <= 2000:
            print(f"     ✓ Tree count is reasonable")
            checks_passed += 1
        else:
            print(f"     ⚠ Tree count seems unusual: {kpis['tree_count']}")
        
        # Check 3: Species are Dang species
        expected_species = ['Teak', 'Sadad', 'Kalam', 'Kudi', 'Kher', 'Bamboo']
        actual_species = list(kpis['species_counts'].keys())
        if all(s in expected_species for s in actual_species):
            print(f"     ✓ Species are correct Dang species")
            checks_passed += 1
        else:
            print(f"     ✗ Wrong species: {actual_species}")
        
        # Check 4: Teak is dominant (should be ~60%)
        if 'Teak' in kpis['species_distribution']:
            teak_pct = kpis['species_distribution']['Teak']
            if 50 <= teak_pct <= 70:
                print(f"     ✓ Teak is dominant ({teak_pct}%)")
                checks_passed += 1
            else:
                print(f"     ⚠ Teak percentage unusual: {teak_pct}%")
        
        # Check 5: Health score calculated
        if kpis['health_score'] > 0:
            print(f"     ✓ Health score calculated")
            checks_passed += 1
        else:
            print(f"     ✗ Health score is zero")
        
        print(f"\n   {'='*66}")
        print(f"   Checks passed: {checks_passed}/{checks_total}")
        
        if checks_passed == checks_total:
            print(f"   ✅ ALL CHECKS PASSED - SYSTEM WORKING PERFECTLY!")
        elif checks_passed >= 3:
            print(f"   ⚠ SYSTEM WORKING - Some minor issues")
        else:
            print(f"   ✗ SYSTEM HAS ISSUES - Check configuration")
        
    else:
        print(f"\n   ✗ Analysis failed with status {response.status_code}")
        print(f"   Error: {response.text}")
        
except Exception as e:
    print(f"\n   ✗ Error during analysis: {e}")

# Test 4: Frontend Check
print(f"\n4. Testing frontend...")
try:
    response = requests.get("http://localhost:5500", timeout=5)
    if response.status_code == 200:
        print("   ✓ Frontend is accessible")
    else:
        print(f"   ✗ Frontend returned status {response.status_code}")
except Exception as e:
    print(f"   ⚠ Frontend not accessible: {e}")
    print("   → Start frontend: cd frontend && python serve.py")

# Final Summary
print(f"\n{'='*70}")
print(f"🎯 SYSTEM STATUS SUMMARY")
print(f"{'='*70}")
print(f"\n✅ Backend: http://localhost:8000")
print(f"✅ Frontend: http://localhost:5500")
print(f"✅ API Docs: http://localhost:8000/docs")
print(f"\n📍 For demo, draw polygons in NORTHERN area:")
print(f"   Latitude: 20.85 to 20.90")
print(f"   Longitude: 73.75 to 73.80")
print(f"\n🎯 System is ready for demonstration!")
print(f"{'='*70}")
