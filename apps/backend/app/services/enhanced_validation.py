"""
Enhanced validation service for improved API input validation and error handling.

Provides comprehensive validation with detailed error messages, field-level
validation, and enhanced user experience through better error reporting.
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from pydantic import BaseModel, ValidationError, Field
from email_validator import validate_email, EmailNotValidError

from app.core.logging_config import get_logger
from app.utils.error_handling import ValidationError as CustomValidationError, ErrorCode

logger = get_logger(__name__)


class ValidationResult(BaseModel):
    """Result of a validation operation."""
    is_valid: bool
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    field_errors: Dict[str, List[str]] = Field(default_factory=dict)
    summary: Optional[str] = None


class FieldValidationRule(BaseModel):
    """Definition of a field validation rule."""
    field_name: str
    rule_type: str
    rule_value: Any = None
    error_message: Optional[str] = None
    warning_message: Optional[str] = None
    is_required: bool = False


class EnhancedValidator:
    """Enhanced validation service with comprehensive error reporting."""
    
    def __init__(self):
        self.logger = get_logger('vessel_guard.validation')
        
        # Predefined validation patterns
        self.patterns = {
            "email": re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
            "phone": re.compile(r'^\+?1?[-.\s]?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})$'),
            "vessel_tag": re.compile(r'^[A-Z0-9]{2,20}$'),
            "project_code": re.compile(r'^[A-Z0-9-]{3,15}$'),
            "alphanumeric": re.compile(r'^[a-zA-Z0-9]+$'),
            "numeric": re.compile(r'^\d+(\.\d+)?$'),
            "safe_text": re.compile(r'^[a-zA-Z0-9\s\-_.,()]+$')
        }
        
        # Engineering validation ranges
        self.engineering_ranges = {
            "pressure": {"min": 0, "max": 10000, "unit": "psi"},
            "temperature": {"min": -273.15, "max": 2000, "unit": "°C"},
            "diameter": {"min": 0.1, "max": 500, "unit": "inches"},
            "thickness": {"min": 0.001, "max": 50, "unit": "inches"},
            "flow_rate": {"min": 0, "max": 100000, "unit": "gpm"},
            "density": {"min": 0.1, "max": 30, "unit": "g/cm³"}
        }
    
    def validate_data(
        self,
        data: Dict[str, Any],
        validation_rules: List[FieldValidationRule],
        context: Optional[Dict[str, Any]] = None
    ) -> ValidationResult:
        """
        Validate data against a set of field validation rules.
        
        Args:
            data: Data to validate
            validation_rules: List of validation rules
            context: Additional context for validation
        
        Returns:
            ValidationResult with detailed error information
        """
        try:
            result = ValidationResult(is_valid=True)
            context = context or {}
            
            # Track processed fields
            processed_fields = set()
            
            # Process each validation rule
            for rule in validation_rules:
                field_name = rule.field_name
                processed_fields.add(field_name)
                
                # Get field value
                field_value = data.get(field_name)
                
                # Check required fields
                if rule.is_required and (field_value is None or field_value == ""):
                    self._add_field_error(
                        result, 
                        field_name, 
                        rule.error_message or f"{field_name} is required"
                    )
                    continue
                
                # Skip validation if field is empty and not required
                if field_value is None or field_value == "":
                    continue
                
                # Apply specific validation rule
                field_result = self._validate_field(field_value, rule, context)
                
                if not field_result.is_valid:
                    result.is_valid = False
                    result.errors.extend(field_result.errors)
                    
                    # Add to field-specific errors
                    if field_name not in result.field_errors:
                        result.field_errors[field_name] = []
                    result.field_errors[field_name].extend([
                        error["message"] for error in field_result.errors
                    ])
                
                # Add warnings
                result.warnings.extend(field_result.warnings)
            
            # Check for unexpected fields
            unexpected_fields = set(data.keys()) - processed_fields
            if unexpected_fields:
                result.warnings.append(
                    f"Unexpected fields found: {', '.join(unexpected_fields)}"
                )
            
            # Generate summary
            if not result.is_valid:
                error_count = len(result.errors)
                field_count = len(result.field_errors)
                result.summary = f"Validation failed with {error_count} errors across {field_count} fields"
            else:
                result.summary = "Validation passed"
                if result.warnings:
                    result.summary += f" with {len(result.warnings)} warnings"
            
            return result
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[{
                    "field": "validation_system",
                    "message": "Internal validation error occurred",
                    "code": "VALIDATION_SYSTEM_ERROR"
                }]
            )
    
    def _validate_field(
        self,
        value: Any,
        rule: FieldValidationRule,
        context: Dict[str, Any]
    ) -> ValidationResult:
        """Validate a single field value against a rule."""
        result = ValidationResult(is_valid=True)
        
        try:
            # Route to specific validation method
            if rule.rule_type == "type":
                self._validate_type(value, rule, result)
            elif rule.rule_type == "length":
                self._validate_length(value, rule, result)
            elif rule.rule_type == "range":
                self._validate_range(value, rule, result)
            elif rule.rule_type == "pattern":
                self._validate_pattern(value, rule, result)
            elif rule.rule_type == "email":
                self._validate_email(value, rule, result)
            elif rule.rule_type == "engineering":
                self._validate_engineering_value(value, rule, result)
            elif rule.rule_type == "custom":
                self._validate_custom(value, rule, result, context)
            elif rule.rule_type == "relationship":
                self._validate_relationship(value, rule, result, context)
            else:
                result.warnings.append(f"Unknown validation rule type: {rule.rule_type}")
            
        except Exception as e:
            self.logger.error(f"Field validation error for {rule.field_name}: {e}")
            self._add_field_error(
                result,
                rule.field_name,
                f"Validation error: {str(e)}"
            )
        
        return result
    
    def _validate_type(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate value type."""
        expected_type = rule.rule_value
        type_map = {
            "string": str,
            "integer": int,
            "float": (int, float),
            "boolean": bool,
            "list": list,
            "dict": dict
        }
        
        if expected_type in type_map:
            expected_python_type = type_map[expected_type]
            if not isinstance(value, expected_python_type):
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"Expected {expected_type}, got {type(value).__name__}",
                    "TYPE_MISMATCH"
                )
    
    def _validate_length(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate value length."""
        if not hasattr(value, '__len__'):
            self._add_validation_error(
                result,
                rule.field_name,
                "Value does not support length validation",
                "LENGTH_NOT_SUPPORTED"
            )
            return
        
        length = len(value)
        rule_value = rule.rule_value
        
        if isinstance(rule_value, dict):
            min_length = rule_value.get("min")
            max_length = rule_value.get("max")
            
            if min_length is not None and length < min_length:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"Minimum length is {min_length}, got {length}",
                    "LENGTH_TOO_SHORT"
                )
            
            if max_length is not None and length > max_length:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"Maximum length is {max_length}, got {length}",
                    "LENGTH_TOO_LONG"
                )
        elif isinstance(rule_value, int):
            if length != rule_value:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"Expected length {rule_value}, got {length}",
                    "LENGTH_MISMATCH"
                )
    
    def _validate_range(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate numeric range."""
        try:
            numeric_value = float(value)
            rule_value = rule.rule_value
            
            if isinstance(rule_value, dict):
                min_val = rule_value.get("min")
                max_val = rule_value.get("max")
                
                if min_val is not None and numeric_value < min_val:
                    self._add_validation_error(
                        result,
                        rule.field_name,
                        rule.error_message or f"Value must be at least {min_val}, got {numeric_value}",
                        "VALUE_TOO_LOW"
                    )
                
                if max_val is not None and numeric_value > max_val:
                    self._add_validation_error(
                        result,
                        rule.field_name,
                        rule.error_message or f"Value must be at most {max_val}, got {numeric_value}",
                        "VALUE_TOO_HIGH"
                    )
        
        except (ValueError, TypeError):
            self._add_validation_error(
                result,
                rule.field_name,
                "Value must be numeric for range validation",
                "NON_NUMERIC_VALUE"
            )
    
    def _validate_pattern(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate against a regex pattern."""
        if not isinstance(value, str):
            self._add_validation_error(
                result,
                rule.field_name,
                "Pattern validation requires string value",
                "PATTERN_TYPE_ERROR"
            )
            return
        
        pattern_name = rule.rule_value
        
        if pattern_name in self.patterns:
            pattern = self.patterns[pattern_name]
            if not pattern.match(value):
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"Value does not match required pattern for {pattern_name}",
                    "PATTERN_MISMATCH"
                )
        else:
            # Treat as custom regex pattern
            try:
                custom_pattern = re.compile(pattern_name)
                if not custom_pattern.match(value):
                    self._add_validation_error(
                        result,
                        rule.field_name,
                        rule.error_message or "Value does not match required pattern",
                        "PATTERN_MISMATCH"
                    )
            except re.error as e:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    f"Invalid regex pattern: {e}",
                    "INVALID_PATTERN"
                )
    
    def _validate_email(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate email address."""
        if not isinstance(value, str):
            self._add_validation_error(
                result,
                rule.field_name,
                "Email must be a string",
                "EMAIL_TYPE_ERROR"
            )
            return
        
        try:
            # Use email-validator library for comprehensive validation
            valid = validate_email(value)
            # Additional checks can be added here
            
        except EmailNotValidError as e:
            self._add_validation_error(
                result,
                rule.field_name,
                rule.error_message or f"Invalid email address: {str(e)}",
                "INVALID_EMAIL"
            )
    
    def _validate_engineering_value(self, value: Any, rule: FieldValidationRule, result: ValidationResult):
        """Validate engineering parameters with unit awareness."""
        parameter_type = rule.rule_value
        
        if parameter_type not in self.engineering_ranges:
            result.warnings.append(f"Unknown engineering parameter type: {parameter_type}")
            return
        
        try:
            numeric_value = float(value)
            ranges = self.engineering_ranges[parameter_type]
            
            if numeric_value < ranges["min"]:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"{parameter_type} must be at least {ranges['min']} {ranges['unit']}",
                    "ENGINEERING_VALUE_TOO_LOW"
                )
            
            if numeric_value > ranges["max"]:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    rule.error_message or f"{parameter_type} must be at most {ranges['max']} {ranges['unit']}",
                    "ENGINEERING_VALUE_TOO_HIGH"
                )
            
            # Add warnings for extreme values
            if numeric_value > ranges["max"] * 0.9:
                result.warnings.append(
                    f"{parameter_type} value {numeric_value} is near maximum limit"
                )
        
        except (ValueError, TypeError):
            self._add_validation_error(
                result,
                rule.field_name,
                f"{parameter_type} must be a numeric value",
                "ENGINEERING_VALUE_NON_NUMERIC"
            )
    
    def _validate_custom(
        self,
        value: Any,
        rule: FieldValidationRule,
        result: ValidationResult,
        context: Dict[str, Any]
    ):
        """Validate using custom logic."""
        custom_rule = rule.rule_value
        
        if isinstance(custom_rule, dict):
            rule_type = custom_rule.get("type")
            
            if rule_type == "date_range":
                self._validate_date_range(value, custom_rule, rule, result)
            elif rule_type == "dependency":
                self._validate_dependency(value, custom_rule, rule, result, context)
            elif rule_type == "unique":
                self._validate_uniqueness(value, custom_rule, rule, result, context)
            else:
                result.warnings.append(f"Unknown custom validation type: {rule_type}")
    
    def _validate_relationship(
        self,
        value: Any,
        rule: FieldValidationRule,
        result: ValidationResult,
        context: Dict[str, Any]
    ):
        """Validate relationships between fields."""
        relationship_rule = rule.rule_value
        
        if isinstance(relationship_rule, dict):
            relationship_type = relationship_rule.get("type")
            target_field = relationship_rule.get("target_field")
            
            if target_field not in context.get("data", {}):
                result.warnings.append(f"Target field {target_field} not found for relationship validation")
                return
            
            target_value = context["data"][target_field]
            
            if relationship_type == "greater_than":
                if float(value) <= float(target_value):
                    self._add_validation_error(
                        result,
                        rule.field_name,
                        rule.error_message or f"{rule.field_name} must be greater than {target_field}",
                        "RELATIONSHIP_VIOLATION"
                    )
            elif relationship_type == "depends_on":
                if target_value is None and value is not None:
                    self._add_validation_error(
                        result,
                        rule.field_name,
                        rule.error_message or f"{rule.field_name} requires {target_field} to be set",
                        "DEPENDENCY_VIOLATION"
                    )
    
    def _validate_date_range(self, value: Any, custom_rule: Dict, rule: FieldValidationRule, result: ValidationResult):
        """Validate date is within acceptable range."""
        try:
            if isinstance(value, str):
                date_value = datetime.fromisoformat(value.replace('Z', '+00:00'))
            elif isinstance(value, datetime):
                date_value = value
            else:
                self._add_validation_error(
                    result,
                    rule.field_name,
                    "Date must be string or datetime object",
                    "DATE_TYPE_ERROR"
                )
                return
            
            min_date = custom_rule.get("min_date")
            max_date = custom_rule.get("max_date")
            
            if min_date and date_value < datetime.fromisoformat(min_date):
                self._add_validation_error(
                    result,
                    rule.field_name,
                    f"Date must be after {min_date}",
                    "DATE_TOO_EARLY"
                )
            
            if max_date and date_value > datetime.fromisoformat(max_date):
                self._add_validation_error(
                    result,
                    rule.field_name,
                    f"Date must be before {max_date}",
                    "DATE_TOO_LATE"
                )
        
        except (ValueError, TypeError) as e:
            self._add_validation_error(
                result,
                rule.field_name,
                f"Invalid date format: {e}",
                "INVALID_DATE_FORMAT"
            )
    
    def _add_field_error(self, result: ValidationResult, field_name: str, message: str):
        """Add a field-specific error to the result."""
        result.is_valid = False
        result.errors.append({
            "field": field_name,
            "message": message,
            "code": "FIELD_ERROR"
        })
    
    def _add_validation_error(
        self,
        result: ValidationResult,
        field_name: str,
        message: str,
        code: str
    ):
        """Add a validation error with specific code."""
        result.is_valid = False
        result.errors.append({
            "field": field_name,
            "message": message,
            "code": code
        })
    
    def validate_calculation_parameters(
        self,
        parameters: Dict[str, Any],
        calculation_type: str
    ) -> ValidationResult:
        """Validate calculation parameters based on calculation type."""
        try:
            # Define validation rules for different calculation types
            rules = self._get_calculation_validation_rules(calculation_type)
            
            # Add context for calculation validation
            context = {
                "calculation_type": calculation_type,
                "data": parameters
            }
            
            return self.validate_data(parameters, rules, context)
            
        except Exception as e:
            self.logger.error(f"Calculation parameter validation failed: {e}")
            return ValidationResult(
                is_valid=False,
                errors=[{
                    "field": "calculation_parameters",
                    "message": f"Validation failed: {str(e)}",
                    "code": "CALCULATION_VALIDATION_ERROR"
                }]
            )
    
    def _get_calculation_validation_rules(self, calculation_type: str) -> List[FieldValidationRule]:
        """Get validation rules for specific calculation types."""
        base_rules = [
            FieldValidationRule(
                field_name="design_pressure",
                rule_type="engineering",
                rule_value="pressure",
                is_required=True,
                error_message="Design pressure is required and must be a valid pressure value"
            ),
            FieldValidationRule(
                field_name="design_temperature",
                rule_type="engineering",
                rule_value="temperature",
                is_required=True,
                error_message="Design temperature is required and must be a valid temperature value"
            )
        ]
        
        # Add calculation-specific rules
        if calculation_type == "pressure_vessel":
            base_rules.extend([
                FieldValidationRule(
                    field_name="diameter",
                    rule_type="engineering",
                    rule_value="diameter",
                    is_required=True
                ),
                FieldValidationRule(
                    field_name="thickness",
                    rule_type="engineering",
                    rule_value="thickness",
                    is_required=True
                ),
                FieldValidationRule(
                    field_name="material",
                    rule_type="type",
                    rule_value="string",
                    is_required=True
                )
            ])
        elif calculation_type == "piping":
            base_rules.extend([
                FieldValidationRule(
                    field_name="pipe_size",
                    rule_type="engineering",
                    rule_value="diameter",
                    is_required=True
                ),
                FieldValidationRule(
                    field_name="flow_rate",
                    rule_type="engineering",
                    rule_value="flow_rate",
                    is_required=True
                )
            ])
        
        return base_rules


# Global validator instance
enhanced_validator = EnhancedValidator()