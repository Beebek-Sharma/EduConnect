"""
Course Data Loader Script
This script loads course data from JSON files into the Django database
"""

import json
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import django

# Setup Django environment
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = script_dir if os.path.exists(os.path.join(script_dir, 'backend')) else os.path.dirname(script_dir)
sys.path.insert(0, os.path.join(project_root, 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from api.models import University, Course

def clean_fees(fees_str):
    """Clean fees data by removing $ and commas"""
    if isinstance(fees_str, str):
        return float(fees_str.replace('$', '').replace(',', ''))
    return float(fees_str)

def load_courses_from_json(json_file_path, clear_existing=False):
    """Load courses from a JSON file"""
    
    if not os.path.exists(json_file_path):
        print(f'⚠️  File not found: {json_file_path}')
        return 0, 0
    
    print(f'\n📂 Processing {os.path.basename(json_file_path)}...')
    
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            courses_data = json.load(f)
        
        created_count = 0
        updated_count = 0
        
        for course_data in courses_data:
            # Extract data from JSON
            university_name = course_data.get('university', '')
            course_name = course_data.get('Course Name', course_data.get('name', ''))
            description = course_data.get('description', '')
            duration = course_data.get('Duration', course_data.get('duration', ''))
            fees_str = course_data.get('Fees', course_data.get('fees', '0'))
            level = course_data.get('Level', course_data.get('level', 'Undergraduate'))
            
            # Clean fees data
            fees = clean_fees(fees_str)
            
            # Get or create university
            university, uni_created = University.objects.get_or_create(
                name=university_name,
                defaults={
                    'description': f'{university_name} - A prestigious institution',
                    'location': 'United States',
                    'ranking': 1,
                    'website': f'https://www.{university_name.lower().replace(" ", "")}.edu',
                }
            )
            
            if uni_created:
                print(f'  🏛️  Created university: {university_name}')
            
            # Create or update course
            course, created = Course.objects.update_or_create(
                name=course_name,
                university=university,
                defaults={
                    'description': description,
                    'duration': duration,
                    'fees': fees,
                    'level': level,
                }
            )
            
            if created:
                created_count += 1
                print(f'  ✅ Created: {course_name}')
            else:
                updated_count += 1
                print(f'  🔄 Updated: {course_name}')
        
        return created_count, updated_count
        
    except json.JSONDecodeError as e:
        print(f'  ❌ JSON Error: {e}')
        return 0, 0
    except Exception as e:
        print(f'  ❌ Error: {e}')
        return 0, 0

def main():
    print("=" * 50)
    print("  Course Data Loader for EduConnect")
    print("=" * 50)
    print()
    
    # JSON files to process
    json_files = [
        'mit.json',
        'harvard_courses.json',
        'stanford.json',
        'ioe_programs.json',
        'ku_programs.json'
    ]
    
    # Ask if user wants to clear existing courses
    try:
        if '--clear' in sys.argv:
            clear = True
        elif '--no-clear' in sys.argv:
            clear = False
        else:
            clear = input('🗑️  Clear existing courses before loading? (y/N): ').lower() == 'y'
    except (EOFError, Exception):
        clear = False
    
    if clear:
        print('\n🗑️  Clearing existing courses...')
        count = Course.objects.all().delete()[0]
        print(f'✅ Deleted {count} courses')
    
    total_created = 0
    total_updated = 0
    
    # Process each JSON file
    for json_file in json_files:
        file_path = os.path.join(project_root, json_file)
        if not os.path.exists(file_path):
            file_path = os.path.join(script_dir, json_file)
        created, updated = load_courses_from_json(file_path, clear)
        total_created += created
        total_updated += updated
    
    # Print summary
    print('\n' + '=' * 50)
    print('📊 SUMMARY:')
    print(f'   ✅ Created: {total_created} courses')
    print(f'   🔄 Updated: {total_updated} courses')
    print(f'   🏛️  Total Universities: {University.objects.count()}')
    print(f'   📖 Total Courses: {Course.objects.count()}')
    print('=' * 50)
    print('\n✅ Course data loading complete!')

if __name__ == '__main__':
    main()
