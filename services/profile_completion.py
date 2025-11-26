"""
Service for calculating profile completion percentage
"""
from typing import Dict, Any
from db.models.user import User
from db.models.annual_target import AnnualTarget
from utils.enums import AnnualTargetStatusEnum


class ProfileCompletionService:
    """Calculate profile completion based on user type"""

    @staticmethod
    def calculate_profile_completion(user: User) -> Dict[str, Any]:
        """
        Calculate profile completion percentage based on user type.

        Returns:
            dict: Profile completion details with percentage
        """
        user_type = user.user_type.value if hasattr(user.user_type, 'value') else user.user_type

        if user_type == "regular":
            return ProfileCompletionService._calculate_regular_user_completion(user)
        elif user_type == "mentor":
            return ProfileCompletionService._calculate_mentor_completion(user)
        elif user_type == "mentee":
            return ProfileCompletionService._calculate_mentee_completion(user)
        else:
            return {
                "total_fields": 0,
                "completed_fields": 0,
                "percentage": 0.0,
                "missing_fields": []
            }

    @staticmethod
    def _calculate_regular_user_completion(user: User) -> Dict[str, Any]:
        """Calculate completion for regular users"""
        fields = {
            # Basic Info (8 fields)
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender,
            "nationality": user.nationality,
            "location": user.location,
            "phone": user.phone,
            "about": user.about,
            # Professional Background (5 fields)
            "current_role": user.current_role,
            "company": user.company,
            "years_of_experience": user.years_of_experience,
            "industry": user.industry,  # List
            "skills": user.skills,  # List
        }

        return ProfileCompletionService._calculate_completion(fields, "regular")

    @staticmethod
    def _calculate_mentor_completion(user: User) -> Dict[str, Any]:
        """Calculate completion for mentors"""
        fields = {
            # Basic Info (8 fields)
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender,
            "nationality": user.nationality,
            "location": user.location,
            "phone": user.phone,
            "about": user.about,
            # Professional Background (5 fields)
            "current_role": user.current_role,
            "company": user.company,
            "years_of_experience": user.years_of_experience,
            "industry": user.industry,
            "skills": user.skills,
            # Mentoring Preferences (2 fields)
            "mentoring_frequency": user.mentoring_frequency,
            "mentoring_format": user.mentoring_format,
        }

        return ProfileCompletionService._calculate_completion(fields, "mentor")

    @staticmethod
    def _calculate_mentee_completion(user: User) -> Dict[str, Any]:
        """Calculate completion for mentees"""
        fields = {
            # Basic Info (8 fields)
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "gender": user.gender,
            "nationality": user.nationality,
            "location": user.location,
            "phone": user.phone,
            "about": user.about,
            # Professional Background (5 fields)
            "current_role": user.current_role,
            "company": user.company,
            "years_of_experience": user.years_of_experience,
            "industry": user.industry,
            "skills": user.skills,
            # Goals (2 fields)
            "career_goals": user.career_goals,
            "long_term_goals": user.long_term_goals,
            # Mentoring Preferences (2 fields)
            "mentoring_frequency": user.mentoring_frequency,
            "mentoring_format": user.mentoring_format,
        }

        return ProfileCompletionService._calculate_completion(fields, "mentee")

    @staticmethod
    def _calculate_completion(fields: Dict[str, Any], user_type: str) -> Dict[str, Any]:
        """Calculate completion percentage from fields"""
        total_fields = len(fields)
        completed_fields = 0
        missing_fields = []

        for field_name, field_value in fields.items():
            if field_value:
                # For lists, check if they have items
                if isinstance(field_value, list):
                    if len(field_value) > 0:
                        completed_fields += 1
                    else:
                        missing_fields.append(field_name)
                else:
                    completed_fields += 1
            else:
                missing_fields.append(field_name)

        percentage = (completed_fields / total_fields * 100) if total_fields > 0 else 0.0

        return {
            "user_type": user_type,
            "total_fields": total_fields,
            "completed_fields": completed_fields,
            "percentage": round(percentage, 2),
            "missing_fields": missing_fields
        }

    @staticmethod
    def calculate_annual_target_completion(annual_targets: list) -> Dict[str, Any]:
        """
        Calculate annual target completion percentage.

        Args:
            annual_targets: List of AnnualTarget objects

        Returns:
            dict: Annual target completion details
        """
        if not annual_targets:
            return {
                "total_targets": 0,
                "completed_targets": 0,
                "in_progress_targets": 0,
                "not_started_targets": 0,
                "overdue_targets": 0,
                "percentage": 0.0
            }

        total = len(annual_targets)
        completed = sum(1 for t in annual_targets if t.status == AnnualTargetStatusEnum.completed)
        in_progress = sum(1 for t in annual_targets if t.status == AnnualTargetStatusEnum.in_progress)
        not_started = sum(1 for t in annual_targets if t.status == AnnualTargetStatusEnum.not_started)
        overdue = sum(1 for t in annual_targets if t.status == AnnualTargetStatusEnum.overdue)

        percentage = (completed / total * 100) if total > 0 else 0.0

        return {
            "total_targets": total,
            "completed_targets": completed,
            "in_progress_targets": in_progress,
            "not_started_targets": not_started,
            "overdue_targets": overdue,
            "percentage": round(percentage, 2)
        }

    @staticmethod
    def calculate_overall_completion(profile_percentage: float, annual_target_percentage: float) -> float:
        """
        Calculate overall profile completion.
        Overall = (Profile Completion + Annual Target Completion) / 2

        Args:
            profile_percentage: Profile completion percentage
            annual_target_percentage: Annual target completion percentage

        Returns:
            float: Overall completion percentage
        """
        overall = (profile_percentage + annual_target_percentage) / 2
        return round(overall, 2)
