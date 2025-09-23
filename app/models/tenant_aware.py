"""
Tenant-Aware Models and Mixins

This module provides the foundation for multi-tenant data isolation
in the Chaknal Platform. It ensures that data is properly segregated
between different companies and organizations.
"""

from sqlalchemy import Column, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, declared_attr
from sqlalchemy.ext.declarative import declared_attr
from typing import Optional
import uuid
from database.base import Base


class TenantAwareMixin:
    """
    Mixin to make models tenant-aware (company-scoped)
    
    This ensures that all data is properly isolated between companies
    and prevents cross-tenant data access.
    """
    
    @declared_attr
    def company_id(cls):
        """Company ID for tenant isolation"""
        return Column(String(36), ForeignKey("company.id"), nullable=False, index=True)
    
    @declared_attr
    def organization_id(cls):
        """Organization ID for enterprise-level grouping"""
        return Column(String(36), ForeignKey("organization.id"), nullable=True, index=True)
    
    @declared_attr
    def is_shared(cls):
        """Whether this record can be shared across tenants"""
        return Column(Boolean, default=False)
    
    @declared_attr
    def company(cls):
        """Relationship to company"""
        return relationship("Company", foreign_keys=[cls.company_id])
    
    @declared_attr
    def organization(cls):
        """Relationship to organization"""
        return relationship("Organization", foreign_keys=[cls.organization_id])


class OrganizationAwareMixin:
    """
    Mixin for organization-level data (shared across companies in same org)
    """
    
    @declared_attr
    def organization_id(cls):
        """Organization ID for organization-level grouping"""
        return Column(String(36), ForeignKey("organization.id"), nullable=False, index=True)
    
    @declared_attr
    def organization(cls):
        """Relationship to organization"""
        return relationship("Organization")


class TenantContext:
    """
    Context manager for tenant operations
    
    This ensures that all database operations are scoped to the current tenant
    and prevents accidental cross-tenant data access.
    """
    
    def __init__(self, company_id: str, organization_id: Optional[str] = None, user_id: Optional[str] = None):
        self.company_id = company_id
        self.organization_id = organization_id
        self.user_id = user_id
        self._previous_context = None
    
    def __enter__(self):
        """Enter tenant context"""
        self._previous_context = get_current_tenant_context()
        set_current_tenant_context(self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit tenant context"""
        if self._previous_context:
            set_current_tenant_context(self._previous_context)
        else:
            clear_current_tenant_context()
    
    def get_tenant_filter(self, model_class):
        """Get tenant filter for a model class"""
        if hasattr(model_class, 'company_id'):
            return model_class.company_id == self.company_id
        return None


# Global tenant context (thread-local storage would be better for production)
_current_tenant_context = None


def get_current_tenant_context() -> Optional[TenantContext]:
    """Get current tenant context"""
    return _current_tenant_context


def set_current_tenant_context(context: TenantContext):
    """Set current tenant context"""
    global _current_tenant_context
    _current_tenant_context = context


def clear_current_tenant_context():
    """Clear current tenant context"""
    global _current_tenant_context
    _current_tenant_context = None


def get_tenant_company_id() -> Optional[str]:
    """Get current tenant company ID"""
    context = get_current_tenant_context()
    return context.company_id if context else None


def get_tenant_organization_id() -> Optional[str]:
    """Get current tenant organization ID"""
    context = get_current_tenant_context()
    return context.organization_id if context else None


def get_tenant_user_id() -> Optional[str]:
    """Get current tenant user ID"""
    context = get_current_tenant_context()
    return context.user_id if context else None


def require_tenant_context():
    """Decorator to require tenant context for functions"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not get_current_tenant_context():
                raise RuntimeError(f"Function {func.__name__} requires tenant context")
            return func(*args, **kwargs)
        return wrapper
    return decorator


def tenant_filter_query(query, model_class):
    """
    Apply tenant filtering to a query
    
    This ensures that queries only return data for the current tenant
    """
    context = get_current_tenant_context()
    if not context:
        raise RuntimeError("No tenant context available")
    
    # Apply company-level filtering
    if hasattr(model_class, 'company_id'):
        query = query.filter(model_class.company_id == context.company_id)
    
    # Apply organization-level filtering if specified
    if context.organization_id and hasattr(model_class, 'organization_id'):
        query = query.filter(model_class.organization_id == context.organization_id)
    
    return query


def create_tenant_aware_record(model_class, **kwargs):
    """
    Create a tenant-aware record with proper tenant context
    
    This ensures that new records are automatically associated with
    the current tenant context.
    """
    context = get_current_tenant_context()
    if not context:
        raise RuntimeError("No tenant context available")
    
    # Automatically set tenant fields
    if hasattr(model_class, 'company_id'):
        kwargs['company_id'] = context.company_id
    
    if context.organization_id and hasattr(model_class, 'organization_id'):
        kwargs['organization_id'] = context.organization_id
    
    return model_class(**kwargs)


class TenantPolicy:
    """
    Tenant access control policies
    
    Defines who can access what data within the multi-tenant system.
    """
    
    def __init__(self, user_role: str, user_company_id: str, user_organization_id: Optional[str] = None):
        self.user_role = user_role
        self.user_company_id = user_company_id
        self.user_organization_id = user_organization_id
    
    def can_access_company_data(self, target_company_id: str) -> bool:
        """Check if user can access company data"""
        # Users can always access their own company data
        if target_company_id == self.user_company_id:
            return True
        
        # Admins can access organization data
        if self.user_role == 'admin' and self.user_organization_id:
            # This would need to check if target company is in same organization
            return True
        
        return False
    
    def can_access_organization_data(self, target_organization_id: str) -> bool:
        """Check if user can access organization data"""
        # Only admins can access organization data
        if self.user_role != 'admin':
            return False
        
        # Users can access their own organization
        if target_organization_id == self.user_organization_id:
            return True
        
        return False
    
    def get_data_scope(self) -> dict:
        """Get the data scope for the current user"""
        scope = {
            'company_id': self.user_company_id,
            'organization_id': self.user_organization_id,
            'can_access_organization': self.user_role == 'admin',
            'can_manage_users': self.user_role in ['admin', 'manager'],
            'can_manage_campaigns': True,  # All users can manage campaigns
            'can_manage_contacts': True,   # All users can manage contacts
        }
        
        return scope


def get_tenant_policy(user: 'User') -> TenantPolicy:
    """Get tenant policy for a user"""
    return TenantPolicy(
        user_role=user.role,
        user_company_id=user.company_id,
        user_organization_id=user.organization_id
    )


# Example usage of tenant-aware models
class TenantAwareContact(Base, TenantAwareMixin):
    """
    Example of a tenant-aware contact model
    
    This shows how to use the TenantAwareMixin to make models
    automatically tenant-isolated.
    """
    __tablename__ = "tenant_contacts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # ... other fields ...
    
    def __init__(self, **kwargs):
        # Ensure tenant context is set
        context = get_current_tenant_context()
        if context and 'company_id' not in kwargs:
            kwargs['company_id'] = context.company_id
        if context and context.organization_id and 'organization_id' not in kwargs:
            kwargs['organization_id'] = context.organization_id
        
        super().__init__(**kwargs)


class TenantAwareCampaign(Base, TenantAwareMixin):
    """
    Example of a tenant-aware campaign model
    """
    __tablename__ = "tenant_campaigns"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # ... other fields ...
    
    def __init__(self, **kwargs):
        # Ensure tenant context is set
        context = get_current_tenant_context()
        if context and 'company_id' not in kwargs:
            kwargs['company_id'] = context.company_id
        if context and context.organization_id and 'organization_id' not in kwargs:
            kwargs['organization_id'] = context.organization_id
        
        super().__init__(**kwargs)
