# Roadmap API Example Usage

## Endpoint: POST /roadmap

### Request Body Examples:

#### 1. Basic Python Learning Roadmap
```json
{
    "topic": "Python Programming",
    "skill_level": "Beginner",
    "time_commitment": "moderate",
    "learning_style": "practical",
    "specific_goals": "Build web applications with Django",
    "userId": "user123"
}
```

#### 2. Advanced Machine Learning Roadmap
```json
{
    "topic": "Machine Learning",
    "skill_level": "Intermediate",
    "time_commitment": "intensive",
    "learning_style": "balanced",
    "specific_goals": "Become proficient in deep learning and neural networks",
    "userId": "user456"
}
```

#### 3. Casual Language Learning
```json
{
    "topic": "Spanish Language",
    "skill_level": "Beginner",
    "time_commitment": "light",
    "learning_style": "visual",
    "specific_goals": "Conversational fluency for travel",
    "userId": "user789"
}
```

### Response Format:
```json
{
    "topic": "Python Programming",
    "total_duration": "3-4 months",
    "difficulty_level": "Beginner",
    "description": "A comprehensive roadmap to master Python programming fundamentals and web development",
    "steps": [
        {
            "step_number": 1,
            "title": "Python Fundamentals",
            "description": "Learn basic Python syntax, variables, data types, and control structures",
            "duration": "2 weeks",
            "difficulty_level": "Beginner",
            "milestones": [
                "Complete Python syntax basics",
                "Write your first Python programs",
                "Understand variables and data types"
            ],
            "resources": [
                "Python.org official tutorial",
                "Codecademy Python course",
                "Python practice problems"
            ],
            "prerequisites": []
        }
        // ... more steps
    ]
}
```

### Features:
1. **Personalized Learning Paths**: Adapts based on skill level and learning preferences
2. **Flexible Time Commitment**: Adjusts pace based on available time (light/moderate/intensive)
3. **Learning Style Adaptation**: Emphasizes resources matching preferred learning style
4. **Progress Tracking**: Saves roadmaps to Firebase for future reference and personalization
5. **Milestone-Based**: Clear, measurable goals for each step
6. **Resource Recommendations**: Curated learning materials for each step
7. **Prerequisite Management**: Ensures proper learning sequence

### Supported Learning Styles:
- **Visual**: Emphasis on diagrams, videos, and visual content
- **Practical**: Focus on hands-on projects and exercises
- **Theoretical**: Comprehensive reading materials and conceptual understanding
- **Balanced**: Mix of all approaches for comprehensive learning

### Time Commitment Options:
- **Light**: 1-2 hours per week, casual learning
- **Moderate**: 3-5 hours per week, steady progress
- **Intensive**: 8+ hours per week, accelerated learning
