from datetime import datetime
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.student import Student
from app.models.course import Course, Lesson
from app.models.assessment import Assessment, Question, StudentAnswer, Result
from app.schemas.assessment import AssessmentSubmission, ResultOut, StudentAnswerOut


def evaluate_submission(
    db: Session,
    assessment_id: int,
    submission: AssessmentSubmission,
    student_id: int,
) -> ResultOut:
    """
    Automatically grades an assessment submission.
    Calculates marks, percentages, topic weaknesses, and personalized recommendations.
    """
    assessment = db.query(Assessment).filter(Assessment.assessment_id == assessment_id).first()
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment with id {assessment_id} not found."
        )

    # Fetch questions for this assessment
    questions = db.query(Question).filter(Question.assessment_id == assessment_id).all()
    if not questions:
        # Fallback to module questions if no direct questions attached
        questions = db.query(Question).join(Course, Assessment.course_id == Course.course_id).all()
    
    question_map: Dict[int, Question] = {q.question_id: q for q in questions}

    total_possible_marks = sum(q.points for q in questions) or assessment.total_marks or 1.0
    student_score = 0.0
    breakdown_list: List[StudentAnswerOut] = []
    topic_performance: Dict[str, Dict[str, int]] = {}  # topic -> {total, correct}

    for item in submission.answers:
        q = question_map.get(item.question_id)
        if not q:
            continue

        raw_student_answer = item.answer.strip()
        raw_correct_answer = q.correct_answer.strip()

        # Automatic evaluation: normalized matching
        # Handles option letters ("A", "B") or exact text values
        is_correct = (raw_student_answer.lower() == raw_correct_answer.lower())
        
        # Check if option matches letter index (e.g., student answers "B", correct is "8" and "8" is option index 1)
        if not is_correct and q.options:
            letter_index = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4}
            # If student entered a letter like 'B'
            if raw_student_answer.lower() in letter_index:
                idx = letter_index[raw_student_answer.lower()]
                if idx < len(q.options) and q.options[idx].strip().lower() == raw_correct_answer.lower():
                    is_correct = True
            # Or if correct answer is stored as letter and student wrote actual text
            if raw_correct_answer.lower() in letter_index:
                idx = letter_index[raw_correct_answer.lower()]
                if idx < len(q.options) and q.options[idx].strip().lower() == raw_student_answer.lower():
                    is_correct = True

        marks_awarded = q.points if is_correct else 0.0
        student_score += marks_awarded

        # Track topic performance
        topic_name = q.topic or "General"
        if topic_name not in topic_performance:
            topic_performance[topic_name] = {"total": 0, "correct": 0}
        topic_performance[topic_name]["total"] += 1
        if is_correct:
            topic_performance[topic_name]["correct"] += 1

        # Save student answer record
        saved_answer = StudentAnswer(
            student_id=student_id,
            assessment_id=assessment_id,
            question_id=q.question_id,
            answer=raw_student_answer,
            is_correct=is_correct,
            marks_awarded=marks_awarded,
            submitted_at=datetime.utcnow(),
        )
        db.add(saved_answer)
        db.flush()

        breakdown_list.append(
            StudentAnswerOut(
                answer_id=saved_answer.answer_id,
                question_id=q.question_id,
                question_text=q.question_text,
                student_answer=raw_student_answer,
                correct_answer=raw_correct_answer,
                is_correct=is_correct,
                marks_awarded=marks_awarded,
                points=q.points,
                topic=topic_name,
            )
        )

    # Scale score to assessment.total_marks
    final_percentage = round((student_score / total_possible_marks) * 100.0, 2) if total_possible_marks > 0 else 0.0
    scaled_score = round((final_percentage / 100.0) * assessment.total_marks, 2)
    passed = final_percentage >= assessment.passing_percentage

    # Identify weak topics (< 60% accuracy)
    weak_topics: List[str] = []
    recommendations: List[str] = []
    for topic, stats in topic_performance.items():
        accuracy = (stats["correct"] / stats["total"]) * 100.0 if stats["total"] > 0 else 0
        if accuracy < 60.0:
            weak_topics.append(topic)
            recommendations.append(f"Review module material on '{topic}' to improve conceptual understanding.")

    if not recommendations:
        if passed:
            recommendations.append("Excellent work! You have mastered the key concepts in this assessment.")
        else:
            recommendations.append("Review the overall course materials and retake practice questions.")

    feedback = (
        f"Passed with {final_percentage}%! Great job."
        if passed
        else f"Score {final_percentage}% is below the passing criteria ({assessment.passing_percentage}%). Keep practicing!"
    )

    result_record = Result(
        student_id=student_id,
        assessment_id=assessment_id,
        score=scaled_score,
        percentage=final_percentage,
        passed=passed,
        feedback=feedback,
        completed_at=datetime.utcnow(),
    )
    db.add(result_record)
    db.commit()
    db.refresh(result_record)

    course_name = assessment.course.course_name if assessment.course else "Unknown Course"

    return ResultOut(
        result_id=result_record.result_id,
        student_id=student_id,
        assessment_id=assessment_id,
        assessment_title=assessment.title,
        course_name=course_name,
        score=scaled_score,
        total_marks=assessment.total_marks,
        percentage=final_percentage,
        passed=passed,
        feedback=feedback,
        completed_at=result_record.completed_at,
        breakdown=breakdown_list,
        weak_topics=weak_topics,
        recommendations=recommendations,
    )
