# TDD Learning Log: Project-Task Relationship
**Date Started:** October 11, 2025, 8:57 PM  
**Branch:** feature/tdd-project-task-relationship  
**Methodology:** Red → Green → Refactor  

## TDD Cycle 1: Basic Relationship
**RED Phase Goal:** Write failing tests for basic Project-Task connection
**GREEN Phase Goal:** Implement minimum code to pass tests  
**REFACTOR Phase Goal:** Clean and optimize implementation

## Business Requirements:
1. Tarea can optionally belong to a Project
2. Project can show list of related tasks
3. Deleting Project should NOT delete tasks (SET_NULL)
4. API should include relationship data

## Learning Objectives:
- Experience complete TDD methodology
- Practice database migrations safely
- Update API serializers accordingly
- Modify templates for new feature

## Success Metrics:
- All tests pass (GREEN)
- Clean, maintainable code
- No regression in existing functionality
- Production deployment successful
