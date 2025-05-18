# Planify - Floor Plan Design System

## Introduction

Planify is a comprehensive floor plan design system that uses a domain-specific language (DSL) to create, visualize, and edit architectural floor plans. This project combines the precision of a programming language with an intuitive web interface, allowing users to design floor plans using code and then interact with the visual representation.

The system is built with a Python backend that handles the parsing and rendering of the DSL code, and a Next.js frontend that provides a user-friendly interface for editing and viewing floor plans. This approach gives users the flexibility to work with either code or visual tools, depending on their preference and the task at hand.

## Features

Planify offers a rich set of features that make it a powerful tool for floor plan design:

- **Domain-Specific Language**: A custom language designed specifically for defining floor plans with intuitive syntax
- **Visual Rendering**: Automatic conversion of DSL code to SVG floor plan visualizations
- **Interactive Editor**: Drag-and-drop interface for modifying floor plan elements
- **Code Synchronization**: Bidirectional sync between visual changes and DSL code
- **Export Options**: Download floor plans as SVG or PNG files

The system supports various element types to create detailed floor plans:

- Rooms with custom properties, dimensions, and labels
- Walls with thickness and connections
- Doors with direction and placement options
- Windows with placement and sizing
- Furniture items (beds, tables, chairs, stairs, elevators)

Additional features include smart layout optimization with automatic conflict resolution, enhanced visual styling, real-world measurement units with automatic scaling, and random floor plan generation for testing and inspiration.

## Architecture Overview

Planify follows a client-server architecture designed for flexibility and performance. The backend, built with Python, provides the core functionality for parsing and rendering floor plans. It processes the DSL code, creates an abstract syntax tree, builds model objects, optimizes the layout, and generates SVG output.

The frontend, developed with Next.js and React, offers a modern and responsive user interface. It includes an interactive code editor, a floor plan viewer with zoom and pan capabilities, and a visual editor for direct manipulation of elements. The frontend communicates with the backend through a REST API, allowing for real-time updates and synchronization between code and visual representations.

This separation of concerns allows for independent development and scaling of each component while maintaining a cohesive user experience.

## Domain-Specific Language

The Planify language is designed to be intuitive yet powerful for defining floor plans. It uses a clean, declarative syntax that makes it easy to understand and write, even for users with limited programming experience.

The language supports structure definitions for rooms, walls, doors, windows, and furniture, with properties for positioning, sizing, and labeling. It also includes control structures like conditional statements and loops, variables and expressions for dynamic calculations, and comments for documentation.

This approach allows users to define complex floor plans programmatically, making it easy to create, duplicate, and modify elements with precision.

## Implementation Details

### Backend

The backend implementation is structured as a pipeline that processes DSL code into rendered floor plans. At its core are four main components:

The **DSL Processing Pipeline** begins with the Lexer, which tokenizes the input code, recognizing language elements like identifiers, literals, and operators. The Parser then constructs an Abstract Syntax Tree (AST) from these tokens, implementing precedence climbing for expressions and providing detailed error reporting. The AST Nodes represent all language constructs, implementing the visitor pattern for traversal. Finally, the Rendering Visitor traverses the AST to build model objects, creating rooms, walls, doors, windows, and furniture.

The **Model Layer** provides a robust representation of floor plan elements. The Room Model represents rooms with properties, calculates areas, and handles dimensions. The Wall Model defines walls with start and end points, calculating length and angle. Door and Window Models are specialized elements with placement on walls, direction, and opening properties. The Furniture Model handles all furniture types with type-specific behaviors. The Floor Plan Model serves as a container for all elements with lookup by ID.

The **Rendering System** transforms models into visual representations. The Renderer handles high-level rendering logic, coordinating element placement and styling. The SVG Exporter provides low-level SVG generation with element drawing primitives. The Style Manager ensures consistent styling with type-specific styles and color palettes. The Layout Manager optimizes element placement, resolving overlaps and placing doors and windows on walls.

The **Web API** exposes the functionality through a FastAPI application with routes for processing DSL code and serving SVG files. The DSL Service handles processing requests, combining parsing, visiting, and rendering to return JSON and SVG output.

### Frontend

The frontend implementation uses Next.js with React to provide an interactive interface for working with floor plans. It is organized around several key components:

The **Core Components** include the Code Editor for syntax-aware text editing with tab handling and line numbers, the Floor Plan Viewer for displaying SVG visualizations with zoom and pan controls, the Floor Plan Editor for interactive element manipulation with selection and property editing, and the Main Page that integrates all components with layout and tab management.

**State Management** is handled by the DSL State, which manages the DSL code and provides random generation, and the API Client, which handles communication with the backend for parsing and rendering requests.

The **UI Components** provide a consistent and accessible user interface with reusable elements like buttons, cards, inputs, and more.

This architecture allows for a seamless user experience, with changes in the code editor immediately reflected in the visual representation and vice versa.

## Basic Workflow

Using PlanifyDSL follows a simple workflow:

1. **Write DSL Code**: Use the code editor to define your floor plan using the DSL.
2. **Parse & Render**: Click the "Parse & Render" button to visualize your floor plan.
3. **Edit Visually**: Switch to the Editor tab to make changes using the visual interface.
4. **Save Changes**: Click "Save Changes" to update the DSL code with your visual edits.
5. **Export**: Download your floor plan as SVG or PNG using the download button.

This bidirectional workflow allows you to work in the way that's most comfortable for you, seamlessly switching between code and visual editing.


## Project Structure

The project is organized into three main directories:

The `DSL/` directory contains the core DSL implementation, including the lexer, parser, and AST in the `Parsing/` subdirectory, domain models in the `Models/` subdirectory, rendering and export functionality in the `Rendering/` subdirectory, AST visitors in the `Visitors/` subdirectory, and layout optimization in the `Layout/` subdirectory.

The `backend/` directory contains the FastAPI backend, with the main application code in the `app/` subdirectory, API routes in the `routers/` subdirectory, and business logic in the `services/` subdirectory.

The `frontend/` directory contains the Next.js frontend, with the source code in the `src/` subdirectory, including the Next.js app router in the `app/` subdirectory, React components in the `components/` subdirectory, and utilities and API client in the `lib/` subdirectory.
