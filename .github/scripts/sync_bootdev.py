#!/usr/bin/env python3
"""
Boot.dev Progress Sync Script
Fetches course completion data from Boot.dev API and updates progress documentation.
"""

import os
import sys
import json
import requests
from datetime import datetime
from typing import Dict, List, Any

# Boot.dev API endpoints
BOOTDEV_USERNAME = os.environ.get('BOOTDEV_USERNAME', 'aott33')
API_BASE = 'https://api.boot.dev/v1'
PUBLIC_PROFILE_URL = f'{API_BASE}/users/public/{BOOTDEV_USERNAME}'
TRACKS_COURSES_URL = f'{API_BASE}/users/public/{BOOTDEV_USERNAME}/tracks_and_courses'

# Progress file paths
PROGRESS_FILE = 'docs/progress/bootdev-progress.md'
STATS_FILE = '.github/bootdev-stats.json'

# Course order for Python & Go track (based on curriculum)
TRACK_COURSE_ORDER = [
    # Main Track
    "Learn Coding Basics",
    "Learn Linux",
    "Learn Git",
    "Build a Bookbot",
    "Learn Object Oriented Programming",
    "Build an Asteroids Game",
    "Learn Functional Programming",
    "Build an AI Agent",
    "Learn Data Structures and Algorithms",
    "Build a Static Site Generator",
    "Learn Memory Management",
    "Personal Project 1",
    "Learn Golang",
    "Learn HTTP Clients",
    "Build a Pokedex",
    "Learn SQL",
    "Build a Blog Aggregator",
    "Learn HTTP Servers",
    "Learn File Storage and CDNs",
    "Learn Docker",
    "Learn Web Security",
    "Learn Pub/Sub Architecture",
    "Learn CI/CD",
    "Learn Kubernetes",
    "Capstone Project",
    "Learn to Find a Job",
    # Deeper Learning (Optional/Advanced)
    "Learn the HTTP Protocol",
    "Learn Git 2",
    "Learn Cryptography",
    "Learn Data Structures and Algorithms 2",
    "Build a Web Scraper"
]

def fetch_json(url: str) -> Dict[str, Any]:
    """Fetch JSON data from URL"""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        sys.exit(1)

def get_profile_data() -> Dict[str, Any]:
    """Fetch public profile data"""
    return fetch_json(PUBLIC_PROFILE_URL)

def get_tracks_and_courses() -> Dict[str, Any]:
    """Fetch tracks and courses data"""
    return fetch_json(TRACKS_COURSES_URL)

def normalize_course_name(name: str) -> str:
    """Normalize course names for matching"""
    # Remove common prefixes/suffixes and normalize
    name = name.replace(" using Python and Pygame", "")
    name = name.replace(" in Python", "").replace(" in Go", "").replace(" in C", "")
    name = name.replace(" in RabbitMQ", "")
    name = name.replace("Learn to Code", "Learn Coding Basics")

    # Handle specific name variations
    if "HTTP Protocol" in name:
        name = "Learn the HTTP Protocol"
    if "Git 2" in name:
        name = "Learn Git 2"
    if "Cryptography" in name:
        name = "Learn Cryptography"
    if "Algorithms 2" in name:
        name = "Learn Data Structures and Algorithms 2"
    if "Web Scraper" in name:
        name = "Build a Web Scraper"
    if "Build Asteroids" in name or "Asteroids" in name:
        name = "Build an Asteroids Game"
    if "Bookbot" in name:
        name = "Build a Bookbot"
    if "AI Agent" in name:
        name = "Build an AI Agent"
    if "Static Site Generator" in name:
        name = "Build a Static Site Generator"
    if "First Personal Project" in name:
        name = "Personal Project 1"

    return name.strip()

def match_course(completed_name: str, track_courses: List[str]) -> str:
    """Find best match for completed course in track"""
    normalized_completed = normalize_course_name(completed_name)

    for track_course in track_courses:
        normalized_track = normalize_course_name(track_course)
        if normalized_completed.lower() in normalized_track.lower() or \
           normalized_track.lower() in normalized_completed.lower():
            return track_course

    return completed_name  # Return original if no match

def calculate_progress(courses_data: List[Dict]) -> tuple:
    """Calculate completion progress"""
    completed_courses = []

    for course in courses_data:
        if course.get('CompletedAt'):
            course_name = course.get('Title', 'Unknown Course')
            matched_name = match_course(course_name, TRACK_COURSE_ORDER)
            completed_courses.append(matched_name)

    total_courses = len(TRACK_COURSE_ORDER)
    completed_count = len(completed_courses)
    percentage = int((completed_count / total_courses) * 100) if total_courses > 0 else 0

    return completed_courses, completed_count, total_courses, percentage

def format_timestamp(iso_string: str) -> str:
    """Format ISO timestamp to readable date"""
    try:
        dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d')
    except:
        return 'Unknown'

def generate_progress_section(profile: Dict, courses_data: List[Dict]) -> str:
    """Generate the auto-updated progress section"""

    # Get profile data
    level = profile.get('Level', 0)
    xp = profile.get('XP', 0)
    role = profile.get('Role', 'Learner')

    # Calculate progress
    completed_courses, completed_count, total_courses, percentage = calculate_progress(courses_data)

    # Build course checklist
    course_checklist = []
    for course_name in TRACK_COURSE_ORDER:
        if course_name in completed_courses:
            # Find course details
            course_data = next((c for c in courses_data if match_course(c.get('Title', ''), [course_name]) == course_name), None)
            if course_data:
                lessons = course_data.get('NumLessons', '?')
                xp_earned = course_data.get('CompletionXp', 0)
                completed_date = format_timestamp(course_data.get('CompletedAt', ''))
                course_checklist.append(f"- [x] **{course_name}** ({lessons} lessons, {xp_earned:,} XP) - Completed {completed_date}")
            else:
                course_checklist.append(f"- [x] **{course_name}**")
        else:
            course_checklist.append(f"- [ ] **{course_name}**")

    # Find next course
    next_course = "Complete!"
    for course in TRACK_COURSE_ORDER:
        if course not in completed_courses:
            next_course = course
            break

    # Current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Generate markdown
    section = f"""## Boot.dev Progress (Auto-Updated)

<!-- AUTO_UPDATE_START -->
**Last Updated:** {current_date}
**Level:** {level} | **Total XP:** {xp:,} | **Role:** {role}

### Track Progress: {percentage}% Complete
**Completed:** {completed_count}/{total_courses} courses

### Course Checklist

{chr(10).join(course_checklist)}

**Next Course:** {next_course}

---

*This section is automatically updated daily via GitHub Actions.*
*Data source: [Boot.dev Public API](https://api.boot.dev/v1/users/public/{BOOTDEV_USERNAME})*
<!-- AUTO_UPDATE_END -->
"""

    return section

def update_progress_file(new_content: str):
    """Update the progress file with new content"""

    # Read existing file
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find markers
    start_marker = '<!-- AUTO_UPDATE_START -->'
    end_marker = '<!-- AUTO_UPDATE_END -->'

    if start_marker in content and end_marker in content:
        # Replace content between markers
        before = content.split(start_marker)[0]
        after = content.split(end_marker)[1]

        # Extract just the inner content (without markers)
        new_inner = new_content.split(start_marker)[1].split(end_marker)[0]

        updated_content = f"{before}{start_marker}{new_inner}{end_marker}{after}"
    else:
        # Markers don't exist, append at the end
        updated_content = content + "\n\n" + new_content

    # Write updated content
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Updated {PROGRESS_FILE}")

def write_stats_json(profile: Dict, courses_data: List[Dict]):
    """Write stats to JSON file for badges"""

    # Calculate progress
    completed_courses, completed_count, total_courses, percentage = calculate_progress(courses_data)

    # Get profile data
    level = profile.get('Level', 0)
    xp = profile.get('XP', 0)
    role = profile.get('Role', 'Learner')

    # Find next course
    next_course = "Complete!"
    for course in TRACK_COURSE_ORDER:
        if course not in completed_courses:
            next_course = course
            break

    # Build stats object
    stats = {
        "schemaVersion": 1,
        "label": "Boot.dev",
        "message": f"{completed_count}/{total_courses} ({percentage}%)",
        "color": "blue",
        "lastUpdated": datetime.now().isoformat(),
        "profile": {
            "username": BOOTDEV_USERNAME,
            "level": level,
            "xp": xp,
            "role": role
        },
        "progress": {
            "coursesCompleted": completed_count,
            "coursesTotal": total_courses,
            "percentageComplete": percentage,
            "nextCourse": next_course
        }
    }

    # Write to file
    with open(STATS_FILE, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2)

    print(f"Updated {STATS_FILE}")

def update_readme_badges(profile: Dict, courses_data: List[Dict]):
    """Update static badges in README.md"""

    # Calculate progress
    completed_courses, completed_count, total_courses, percentage = calculate_progress(courses_data)

    # Get profile data
    level = profile.get('Level', 0)

    # Read README
    with open('README.md', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find and replace badge lines
    import re

    # Update Level badge
    content = re.sub(
        r'\[!\[Boot\.dev Level\]\(https://img\.shields\.io/badge/Boot\.dev-Level%20\d+-blueviolet\)\]',
        f'[![Boot.dev Level](https://img.shields.io/badge/Boot.dev-Level%20{level}-blueviolet)]',
        content
    )

    # Update Courses badge
    content = re.sub(
        r'\[!\[Boot\.dev Courses\]\(https://img\.shields\.io/badge/Courses-[^\]]+\)\]',
        f'[![Boot.dev Courses](https://img.shields.io/badge/Courses-{completed_count}%2F{total_courses}%20({percentage}%25)-blue)]',
        content
    )

    # Write back
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Updated README.md badges")

def main():
    """Main execution"""
    print("Fetching Boot.dev progress...")

    # Fetch data
    profile_response = get_profile_data()
    tracks_courses_response = get_tracks_and_courses()

    # Extract data from response (API returns {"data": {...}, "status": "success"})
    profile = profile_response.get('data', {})
    courses_data = tracks_courses_response.get('data', {}).get('Courses', [])

    if not courses_data:
        print("No course data found", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(courses_data)} courses")

    # Generate new content
    new_section = generate_progress_section(profile, courses_data)

    # Update files
    update_progress_file(new_section)
    write_stats_json(profile, courses_data)
    update_readme_badges(profile, courses_data)

    print("Progress sync complete!")

if __name__ == "__main__":
    main()
