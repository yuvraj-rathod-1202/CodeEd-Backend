"""
Utility functions for creating personalized prompts based on user details
"""

from typing import Optional, Dict, Any, List
from app.services.firebase.get_persionalized_content import get_personalized_content
from app.models.BaseModel.personalized.personal import Personalized_User_Content, Personalized_Content, Personalized_Quiz, Personalized_Flowchart


def get_quiz_performance_insights(quizzes: List[Personalized_Quiz]) -> List[str]:
    """
    Analyze quiz performance patterns and return insights.
    
    Args:
        quizzes: List of personalized quiz data
        
    Returns:
        List[str]: Performance insights for personalization
    """
    if not quizzes:
        return []
    
    insights = []
    
    try:
        # Calculate overall performance metrics
        total_questions = sum(quiz.total_questions for quiz in quizzes)
        total_correct = sum(quiz.correct_answers for quiz in quizzes)
        total_incorrect = sum(quiz.incorrect_answers for quiz in quizzes)
        
        if total_questions > 0:
            accuracy = (total_correct / total_questions) * 100
            
            if accuracy >= 85:
                insights.append(f"Quiz Performance: Excellent ({accuracy:.0f}% accuracy across {len(quizzes)} recent quizzes)")
            elif accuracy >= 70:
                insights.append(f"Quiz Performance: Good ({accuracy:.0f}% accuracy, room for improvement)")
            elif accuracy >= 50:
                insights.append(f"Quiz Performance: Average ({accuracy:.0f}% accuracy, needs focus on weak areas)")
            else:
                insights.append(f"Quiz Performance: Needs improvement ({accuracy:.0f}% accuracy, requires more practice)")
        
        # Analyze difficulty preferences
        difficulty_counts = {}
        for quiz in quizzes:
            difficulty = quiz.difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        if difficulty_counts:
            preferred_difficulty = max(difficulty_counts.items(), key=lambda x: x[1])[0]
            insights.append(f"Preferred Difficulty: {preferred_difficulty} level questions")
        
        # Analyze quiz types
        quiz_type_counts = {}
        for quiz in quizzes:
            quiz_type = quiz.quiz_type
            quiz_type_counts[quiz_type] = quiz_type_counts.get(quiz_type, 0) + 1
        
        if quiz_type_counts:
            preferred_type = max(quiz_type_counts.items(), key=lambda x: x[1])[0]
            insights.append(f"Preferred Quiz Type: {preferred_type} questions")
        
        # Analyze time patterns
        avg_time_per_question = []
        for quiz in quizzes:
            if quiz.time_taken and quiz.total_questions > 0:
                avg_time = sum(quiz.time_taken) / len(quiz.time_taken) if quiz.time_taken else 0
                avg_time_per_question.append(avg_time / quiz.total_questions if avg_time > 0 else 0)
        
        if avg_time_per_question:
            avg_time = sum(avg_time_per_question) / len(avg_time_per_question)
            if avg_time > 120:  # More than 2 minutes per question
                insights.append("Learning Style: Takes time to think through questions carefully")
            elif avg_time < 30:  # Less than 30 seconds per question
                insights.append("Learning Style: Quick decision maker, prefers fast-paced content")
            else:
                insights.append("Learning Style: Balanced approach to question-solving")
        
    except Exception as e:
        print(f"Error analyzing quiz performance: {e}")
    
    return insights


def get_flowchart_pattern_insights(flowcharts: List[Personalized_Flowchart]) -> List[str]:
    """
    Analyze flowchart creation patterns and return insights.
    
    Args:
        flowcharts: List of personalized flowchart data
        
    Returns:
        List[str]: Flowchart pattern insights for personalization
    """
    if not flowcharts:
        return []
    
    insights = []
    
    try:
        # Analyze complexity preferences
        total_nodes = sum(chart.node_count for chart in flowcharts if hasattr(chart, 'node_count'))
        avg_nodes = total_nodes / len(flowcharts) if flowcharts else 0
        
        if avg_nodes > 0:
            if avg_nodes >= 15:
                insights.append("Flowchart Style: Prefers detailed, comprehensive visual representations")
            elif avg_nodes >= 8:
                insights.append("Flowchart Style: Likes moderate complexity with good structure")
            else:
                insights.append("Flowchart Style: Prefers simple, concise visual summaries")
        
        # Analyze recent flowchart topics/titles
        recent_titles = [chart.title for chart in flowcharts[-3:] if hasattr(chart, 'title') and chart.title]
        if recent_titles:
            insights.append(f"Recent Flowchart Topics: {', '.join(recent_titles[:2])}")
        
        # Analyze frequency of flowchart creation
        if len(flowcharts) >= 5:
            insights.append("Visual Learning: Frequently uses flowcharts for understanding concepts")
        elif len(flowcharts) >= 2:
            insights.append("Visual Learning: Occasionally uses flowcharts for complex topics")
        else:
            insights.append("Visual Learning: New to using flowcharts for learning")
        
    except Exception as e:
        print(f"Error analyzing flowchart patterns: {e}")
    
    return insights


def get_quiz_based_instructions(quizzes: List[Personalized_Quiz]) -> List[str]:
    """
    Generate personalization instructions based on quiz history.
    
    Args:
        quizzes: List of personalized quiz data
        
    Returns:
        List[str]: Instructions based on quiz patterns
    """
    if not quizzes:
        return []
    
    instructions = []
    
    try:
        # Performance-based instructions
        total_questions = sum(quiz.total_questions for quiz in quizzes)
        total_correct = sum(quiz.correct_answers for quiz in quizzes)
        
        if total_questions > 0:
            accuracy = (total_correct / total_questions) * 100
            
            if accuracy < 60:
                instructions.append("Provide more detailed explanations and examples to reinforce understanding")
                instructions.append("Include easier questions to build confidence before advancing")
            elif accuracy > 85:
                instructions.append("Challenge the user with more complex questions and advanced concepts")
                instructions.append("Focus on application and analysis rather than basic recall")
        
        # Difficulty preference instructions
        difficulty_counts = {}
        for quiz in quizzes:
            difficulty = quiz.difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1
        
        if difficulty_counts:
            most_attempted = max(difficulty_counts.items(), key=lambda x: x[1])[0]
            if most_attempted == "Easy":
                instructions.append("Gradually introduce intermediate concepts with clear explanations")
            elif most_attempted == "Hard":
                instructions.append("Provide challenging content with deep analytical questions")
        
        # Quiz type preferences
        quiz_type_counts = {}
        for quiz in quizzes:
            quiz_type = quiz.quiz_type
            quiz_type_counts[quiz_type] = quiz_type_counts.get(quiz_type, 0) + 1
        
        if quiz_type_counts:
            preferred_type = max(quiz_type_counts.items(), key=lambda x: x[1])[0]
            if preferred_type == "mcq":
                instructions.append("Include multiple-choice questions with clear, distinct options")
            elif preferred_type == "truefalse":
                instructions.append("Use true/false format for quick concept verification")
            elif preferred_type == "shortanswer":
                instructions.append("Encourage descriptive answers and critical thinking")
        
    except Exception as e:
        print(f"Error generating quiz-based instructions: {e}")
    
    return instructions


def get_flowchart_based_instructions(flowcharts: List[Personalized_Flowchart]) -> List[str]:
    """
    Generate personalization instructions based on flowchart history.
    
    Args:
        flowcharts: List of personalized flowchart data
        
    Returns:
        List[str]: Instructions based on flowchart patterns
    """
    if not flowcharts:
        return []
    
    instructions = []
    
    try:
        # Complexity preferences
        total_nodes = sum(chart.node_count for chart in flowcharts if hasattr(chart, 'node_count'))
        avg_nodes = total_nodes / len(flowcharts) if flowcharts else 0
        
        if avg_nodes > 0:
            if avg_nodes >= 15:
                instructions.append("Create detailed, comprehensive flowcharts with multiple levels and connections")
                instructions.append("Include sub-processes and detailed breakdowns in visual representations")
            elif avg_nodes >= 8:
                instructions.append("Balance detail and simplicity in flowcharts - moderate complexity works well")
            else:
                instructions.append("Keep flowcharts simple and focused on main concepts for better comprehension")
        
        # Usage frequency insights
        if len(flowcharts) >= 5:
            instructions.append("User benefits greatly from visual learning - prioritize flowcharts and diagrams")
            instructions.append("Break down complex processes into visual step-by-step representations")
        elif len(flowcharts) >= 2:
            instructions.append("Include visual elements when explaining complex topics")
        
        # Recent pattern analysis
        if len(flowcharts) >= 3:
            recent_complexity = sum(chart.node_count for chart in flowcharts[-3:] if hasattr(chart, 'node_count'))
            early_complexity = sum(chart.node_count for chart in flowcharts[:3] if hasattr(chart, 'node_count'))
            
            if recent_complexity > early_complexity * 1.2:
                instructions.append("User is progressing to more complex visual representations - increase detail appropriately")
            elif recent_complexity < early_complexity * 0.8:
                instructions.append("User prefers simpler visual formats - focus on clarity over complexity")
        
    except Exception as e:
        print(f"Error generating flowchart-based instructions: {e}")
    
    return instructions


def get_learning_pattern_insights(personalized_content: Personalized_Content) -> List[str]:
    """
    Get comprehensive learning pattern insights from both quizzes and flowcharts.
    
    Args:
        personalized_content: Complete personalized content data
        
    Returns:
        List[str]: Learning pattern insights
    """
    insights = []
    
    try:
        quizzes = personalized_content.personalized_quiz.quizzes
        flowcharts = personalized_content.personalized_flowchart.flowcharts
        
        # Overall engagement patterns
        total_activities = len(quizzes) + len(flowcharts)
        if total_activities >= 10:
            insights.append("Learning Pattern: Highly engaged learner with consistent practice")
        elif total_activities >= 5:
            insights.append("Learning Pattern: Regular learner with moderate engagement")
        elif total_activities >= 2:
            insights.append("Learning Pattern: Occasional learner exploring different formats")
        else:
            insights.append("Learning Pattern: New to the platform, building learning habits")
        
        # Learning modality preferences
        quiz_count = len(quizzes)
        flowchart_count = len(flowcharts)
        
        if quiz_count > flowchart_count * 2:
            insights.append("Learning Style: Prefers assessment-based learning and testing knowledge")
        elif flowchart_count > quiz_count * 2:
            insights.append("Learning Style: Visual learner who prefers structured representations")
        elif quiz_count > 0 and flowchart_count > 0:
            insights.append("Learning Style: Balanced approach using both assessment and visual learning")
        
        # Progress tracking
        if quizzes and len(quizzes) >= 3:
            recent_scores = []
            for quiz in quizzes[-3:]:
                if quiz.total_questions > 0:
                    score = (quiz.correct_answers / quiz.total_questions) * 100
                    recent_scores.append(score)
            
            if len(recent_scores) >= 2:
                if recent_scores[-1] > recent_scores[0] + 10:
                    insights.append("Progress Trend: Showing improvement in recent assessments")
                elif recent_scores[-1] < recent_scores[0] - 10:
                    insights.append("Progress Trend: May need additional support or review")
                else:
                    insights.append("Progress Trend: Consistent performance level maintained")
        
    except Exception as e:
        print(f"Error analyzing learning patterns: {e}")
    
    return insights


def get_user_context_string(userId: Optional[str] = None, user_context: Optional[Personalized_Content] = None) -> str:
    if not userId:
        return ""
    
    try:
        # Get personalized content for the user
        personalized_content = user_context if user_context else get_personalized_content(userId)
        user_info = personalized_content.personalized_info
        
        # Create context string
        context_parts = []
        
        if user_info.experience != "Not Specified":
            context_parts.append(f"Experience Level: {user_info.experience}")
        
        if user_info.goal != "General Learning":
            context_parts.append(f"Learning Goal: {user_info.goal}")
        
        if user_info.education != "Not Specified":
            context_parts.append(f"Educational Background: {user_info.education}")
        
        if user_info.interests and user_info.interests != ["General"]:
            interests_str = ", ".join(user_info.interests)
            context_parts.append(f"Areas of Interest: {interests_str}")
        
        if user_info.country != "Unknown":
            context_parts.append(f"Location: {user_info.country}")
        
        # Add quiz performance insights
        quiz_insights = get_quiz_performance_insights(personalized_content.personalized_quiz.quizzes)
        if quiz_insights:
            context_parts.extend(quiz_insights)
        
        # Add flowchart pattern insights
        flowchart_insights = get_flowchart_pattern_insights(personalized_content.personalized_flowchart.flowcharts)
        if flowchart_insights:
            context_parts.extend(flowchart_insights)
        
        # Add comprehensive learning pattern insights
        learning_pattern_insights = get_learning_pattern_insights(personalized_content)
        if learning_pattern_insights:
            context_parts.extend(learning_pattern_insights)
        
        if context_parts:
            return "\n".join([
                "\n📝 User Profile Context:",
                *[f"   • {part}" for part in context_parts],
                ""
            ])
        
        return ""
        
    except Exception as e:
        print(f"Error getting user context: {e}")
        return ""


def get_personalization_instructions(userId: Optional[str] = None, user_context: Optional[Personalized_Content] = None) -> str:
    if not userId:
        return ""
    
    try:
        personalized_content = user_context if user_context else get_personalized_content(userId)
        user_info = personalized_content.personalized_info
        
        instructions = []
        
        # Experience-based instructions
        if user_info.experience == "Beginner":
            instructions.append("Use simple, beginner-friendly language and provide extra explanations for technical terms")
        elif user_info.experience == "Intermediate":
            instructions.append("Use moderately technical language and provide balanced detail")
        elif user_info.experience == "Advanced":
            instructions.append("Use advanced terminology and focus on deeper insights")
        
        # Goal-based instructions
        if "exam" in user_info.goal.lower() or "test" in user_info.goal.lower():
            instructions.append("Focus on testable concepts and include exam-style questions")
        elif "career" in user_info.goal.lower() or "job" in user_info.goal.lower():
            instructions.append("Emphasize practical applications and real-world scenarios")
        elif "research" in user_info.goal.lower():
            instructions.append("Include detailed analysis and references to further study")
        elif "hobby" in user_info.goal.lower() or "personal interest" in user_info.goal.lower():
            instructions.append("Make the content engaging and fun, with interesting examples")
        elif "general learning" in user_info.goal.lower():
            instructions.append("Provide a broad overview of concepts and encourage exploration")

        # Education-based instructions
        if "high school" in user_info.education.lower():
            instructions.append("Relate concepts to high school level understanding")
        elif "bachelor" in user_info.education.lower():
            instructions.append("Use undergraduate level concepts and examples")
        elif "master" in user_info.education.lower() or "phd" in user_info.education.lower():
            instructions.append("Include advanced concepts and theoretical frameworks")
        elif "self-taught" in user_info.education.lower():
            instructions.append("Provide clear, step-by-step explanations suitable for self-learners")
        
        
        # Interest-based instructions
        if user_info.interests and user_info.interests != ["General"]:
            interests_str = ", ".join(user_info.interests)
            instructions.append(f"When possible, relate concepts to the user's interests: {interests_str}")
        
        # Add quiz-based personalization
        quiz_based_instructions = get_quiz_based_instructions(personalized_content.personalized_quiz.quizzes)
        instructions.extend(quiz_based_instructions)
        
        # Add flowchart-based personalization
        flowchart_based_instructions = get_flowchart_based_instructions(personalized_content.personalized_flowchart.flowcharts)
        instructions.extend(flowchart_based_instructions)
        
        if instructions:
            return "\n🎯 Personalization Guidelines:\n" + "\n".join([f"   • {inst}" for inst in instructions]) + "\n"
        
        return ""
        
    except Exception as e:
        print(f"Error getting personalization instructions: {e}")
        return ""


def create_personalized_prompt_prefix(userId: Optional[str] = None, user_contex: Optional[Personalized_Content] = None) -> str:
    """
    Create a personalized prompt prefix including user context and instructions.
    
    Args:
        userId: Optional user ID to get personalized content
        
    Returns:
        str: Complete personalized prompt prefix
    """
    if not userId:
        return ""

    user_context = get_user_context_string(userId, user_context=user_contex)
    personalization_instructions = get_personalization_instructions(userId, user_context=user_contex)

    if user_context or personalization_instructions:
        return user_context + personalization_instructions
    
    return ""


def enhance_prompt_with_personalization(base_prompt: str, userId: Optional[str] = None) -> str:
    """
    Enhance a base prompt with personalization based on user profile.
    
    Args:
        base_prompt: The original prompt
        userId: Optional user ID for personalization
        
    Returns:
        str: Enhanced prompt with personalization
    """
    if not userId:
        return base_prompt

    user_personalization_context = get_personalized_content(userId)
    personalized_prefix = create_personalized_prompt_prefix(userId, user_personalization_context)
    
    if personalized_prefix:
        return personalized_prefix + "\n" + base_prompt
    
    return base_prompt
