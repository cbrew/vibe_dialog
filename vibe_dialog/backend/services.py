"""Services for the vibe_dialog system."""
import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, BinaryIO, Set

import hashlib
from werkzeug.utils import secure_filename

from vibe_dialog.backend.models import (
    AnnotationType,
    Annotation,
    Citation,
    DialogueContext,
    Document,
    MessageRole,
    SearchProvider,
    SearchResult,
    UserProfile,
)


class DialogueService:
    """Service for managing dialogue interactions."""

    def __init__(self) -> None:
        """Initialize the dialogue service."""
        self.active_contexts: Dict[str, DialogueContext] = {}

    def create_context(self, user_profile: Optional[UserProfile] = None) -> str:
        """Create a new dialogue context."""
        context_id = str(uuid.uuid4())
        context = DialogueContext(id=context_id, user_profile=user_profile)
        self.active_contexts[context_id] = context
        return context_id

    def get_context(self, context_id: str) -> Optional[DialogueContext]:
        """Get a dialogue context by ID."""
        return self.active_contexts.get(context_id)

    def add_user_message(
        self, 
        context_id: str, 
        content: str,
        citations: Optional[List[Citation]] = None,
        referenced_documents: Optional[List[str]] = None,
    ) -> bool:
        """Add a user message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(
                MessageRole.USER, 
                content, 
                citations=citations,
                referenced_documents=referenced_documents,
            )
            return True
        return False

    def add_system_message(
        self, 
        context_id: str, 
        content: str,
        citations: Optional[List[Citation]] = None,
        referenced_documents: Optional[List[str]] = None,
    ) -> bool:
        """Add a system message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(
                MessageRole.SYSTEM, 
                content, 
                citations=citations,
                referenced_documents=referenced_documents,
            )
            return True
        return False

    def add_assistant_message(
        self, 
        context_id: str, 
        content: str,
        citations: Optional[List[Citation]] = None,
        referenced_documents: Optional[List[str]] = None,
    ) -> bool:
        """Add an assistant message to the dialogue."""
        context = self.get_context(context_id)
        if context:
            context.add_message(
                MessageRole.ASSISTANT, 
                content, 
                citations=citations,
                referenced_documents=referenced_documents,
            )
            return True
        return False

    def set_active_document(
        self, context_id: str, document_id: Optional[str]
    ) -> bool:
        """Set the active document for the context."""
        context = self.get_context(context_id)
        if context:
            return context.set_active_document(document_id)
        return False

    def store_search_results(
        self, context_id: str, query: str, results: List[SearchResult]
    ) -> bool:
        """Store search results in the context."""
        context = self.get_context(context_id)
        if context:
            context.search_documents(query, results)
            return True
        return False

    def clear_search_results(
        self, context_id: str, query: Optional[str] = None
    ) -> bool:
        """Clear search results for a query or all queries."""
        context = self.get_context(context_id)
        if context:
            context.clear_search_results(query)
            return True
        return False

    def save_context(self, context_id: str) -> bool:
        """Save the dialogue context."""
        # In a real implementation, this would persist the context to a database
        context = self.get_context(context_id)
        if context:
            # Placeholder for saving logic
            return True
        return False

    def close_context(self, context_id: str) -> bool:
        """Close and remove a dialogue context."""
        if context_id in self.active_contexts:
            del self.active_contexts[context_id]
            return True
        return False


class DocumentService:
    """Service for managing documents."""
    
    # Default upload directory relative to the application root
    UPLOAD_DIR = Path("uploads")
    
    def __init__(self) -> None:
        """Initialize the document service."""
        # Create upload directory if it doesn't exist
        self.UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
        
    def create_document(
        self, 
        title: str, 
        content: str, 
        metadata: Optional[Dict] = None,
        file: Any = None, 
        file_name: Optional[str] = None, 
        file_type: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> Document:
        """Create a new document."""
        doc_id = str(uuid.uuid4())
        now = datetime.now()
        
        # File handling
        file_path = None
        file_size = None
        
        if file and file_name:
            secure_name = secure_filename(file_name)
            # Generate a unique filename with uuid to prevent collisions
            unique_filename = f"{doc_id}_{secure_name}"
            file_path = str(self.UPLOAD_DIR / unique_filename)
            
            # If the file is a file-like object, save it
            if hasattr(file, 'read'):
                if hasattr(file, 'save'):
                    file.save(file_path)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(file.read())
                file_size = os.path.getsize(file_path)
            # If the file is a path string, move or copy it
            elif isinstance(file, str) and os.path.isfile(file):
                os.replace(file, file_path)
                file_size = os.path.getsize(file_path)
        
        document = Document(
            id=doc_id,
            title=title,
            content=content,
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            metadata=metadata or {},
            tags=tags or set(),
            created_at=now,
            updated_at=now,
        )
        return document

    def update_document(
        self,
        document: Document,
        title: Optional[str] = None,
        content: Optional[str] = None,
        file: Any = None, 
        file_name: Optional[str] = None,
        file_type: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> Document:
        """Update a document."""
        if title is not None:
            document.title = title
        if content is not None:
            document.content = content
        if tags is not None:
            document.tags = tags
            
        # Update file if provided
        if file and file_name:
            # Remove old file if it exists
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
                
            secure_name = secure_filename(file_name)
            # Generate a unique filename with uuid to prevent collisions
            unique_filename = f"{document.id}_{secure_name}"
            file_path = str(self.UPLOAD_DIR / unique_filename)
            
            # If the file is a file-like object, save it
            if hasattr(file, 'read'):
                if hasattr(file, 'save'):
                    file.save(file_path)
                else:
                    with open(file_path, 'wb') as f:
                        f.write(file.read())
                file_size = os.path.getsize(file_path)
            # If the file is a path string, move or copy it
            elif isinstance(file, str) and os.path.isfile(file):
                os.replace(file, file_path)
                file_size = os.path.getsize(file_path)
                
            document.file_path = file_path
            document.file_name = file_name
            document.file_type = file_type
            document.file_size = file_size
            
        document.updated_at = datetime.now()
        return document

    def create_citation(
        self,
        text: str,
        source: str,
        page: Optional[int] = None,
        section: Optional[str] = None,
        url: Optional[str] = None,
    ) -> Citation:
        """Create a new citation."""
        # Create a unique ID based on content hash
        hash_input = f"{text}|{source}|{page}|{section}|{url}"
        citation_id = hashlib.md5(hash_input.encode()).hexdigest()[:16]
        
        return Citation(
            id=citation_id,
            text=text,
            source=source,
            page=page,
            section=section,
            url=url,
        )

    def create_annotation(
        self,
        document_id: str,
        annotation_type: AnnotationType,
        text: str,
        position: Dict[str, Union[int, str]],
        user_id: Optional[str] = None,
        color: Optional[str] = None,
        citations: Optional[List[Citation]] = None,
    ) -> Annotation:
        """Create a new annotation."""
        annotation_id = str(uuid.uuid4())
        now = datetime.now()
        
        return Annotation(
            id=annotation_id,
            type=annotation_type,
            text=text,
            position=position,
            document_id=document_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
            color=color,
            citations=citations or [],
        )

    def add_annotation_to_document(
        self, document: Document, annotation: Annotation
    ) -> Document:
        """Add an annotation to a document."""
        document.add_annotation(annotation)
        return document

    def remove_annotation_from_document(
        self, document: Document, annotation_id: str
    ) -> bool:
        """Remove an annotation from a document."""
        return document.remove_annotation(annotation_id)

    def add_citation_to_document(
        self, document: Document, citation: Citation
    ) -> Document:
        """Add a citation to a document."""
        document.add_citation(citation)
        return document

    def add_tag_to_document(self, document: Document, tag: str) -> Document:
        """Add a tag to a document."""
        document.add_tag(tag)
        return document

    def remove_tag_from_document(
        self, document: Document, tag: str
    ) -> bool:
        """Remove a tag from a document."""
        return document.remove_tag(tag)
        
    def get_file_path(self, document: Document) -> Optional[str]:
        """Get the full file path for a document's attached file."""
        if document.file_path and os.path.exists(document.file_path):
            return document.file_path
        return None
        
    def delete_file(self, document: Document) -> bool:
        """Delete a document's attached file."""
        if document.file_path and os.path.exists(document.file_path):
            os.remove(document.file_path)
            document.file_path = None
            document.file_name = None
            document.file_type = None
            document.file_size = None
            document.updated_at = datetime.now()
            return True
        return False
        
    # Backward compatibility methods
    
    def add_comment(self, document: Document, comment: str) -> Document:
        """Add a comment to a document (backward compatibility method)."""
        document.comments.append(comment)
        document.updated_at = datetime.now()
        return document
        
    def add_citation(self, document: Document, citation: str) -> Document:
        """Add a citation string to a document (backward compatibility method)."""
        citation_obj = self.create_citation(citation, "Unknown source")
        document.citations.append(citation_obj)
        document.updated_at = datetime.now()
        return document

class SearchService:
    """Service for searching documents."""
    
    def __init__(self, default_provider: SearchProvider = SearchProvider.LOCAL) -> None:
        """Initialize the search service."""
        self.default_provider = default_provider
    
    def search(
        self,
        query: str,
        documents: Dict[str, Document],
        provider: Optional[SearchProvider] = None,
        max_results: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """Search documents using the specified provider."""
        provider = provider or self.default_provider
        filters = filters or {}
        
        # Filter documents based on filters if any
        filtered_docs = self._apply_filters(documents, filters)
        
        if provider == SearchProvider.LOCAL:
            return self._local_search(query, filtered_docs, max_results)
        elif provider == SearchProvider.SEMANTIC:
            return self._semantic_search(query, filtered_docs, max_results)
        elif provider == SearchProvider.HYBRID:
            return self._hybrid_search(query, filtered_docs, max_results)
        else:
            # Default to local search
            return self._local_search(query, filtered_docs, max_results)
    
    def _apply_filters(
        self, documents: Dict[str, Document], filters: Dict[str, Any]
    ) -> Dict[str, Document]:
        """Apply filters to documents."""
        if not filters:
            return documents
            
        filtered_docs = {}
        
        for doc_id, doc in documents.items():
            include = True
            
            # Filter by tags
            if 'tags' in filters and filters['tags']:
                # Check if document has any of the specified tags
                if not any(tag in doc.tags for tag in filters['tags']):
                    include = False
                    
            # Filter by date range
            if 'date_from' in filters and filters['date_from']:
                try:
                    date_from = datetime.fromisoformat(filters['date_from'])
                    if doc.created_at < date_from:
                        include = False
                except (ValueError, TypeError):
                    pass
                    
            if 'date_to' in filters and filters['date_to']:
                try:
                    date_to = datetime.fromisoformat(filters['date_to'])
                    if doc.created_at > date_to:
                        include = False
                except (ValueError, TypeError):
                    pass
                    
            # Filter by has_file
            if 'has_file' in filters:
                if filters['has_file'] and not doc.file_path:
                    include = False
                elif filters['has_file'] is False and doc.file_path:
                    include = False
                    
            # Include document if it passes all filters
            if include:
                filtered_docs[doc_id] = doc
                
        return filtered_docs
    
    def _local_search(
        self, query: str, documents: Dict[str, Document], max_results: int
    ) -> List[SearchResult]:
        """Perform a simple text-based search on documents."""
        results = []
        query_lower = query.lower()
        
        for doc_id, doc in documents.items():
            # Check in title
            if query_lower in doc.title.lower():
                results.append(
                    SearchResult(
                        document_id=doc_id,
                        relevance_score=1.0,  # High relevance for title matches
                        matched_text=doc.title,
                        context=doc.title,
                    )
                )
                
            # Check in content
            content_lower = doc.content.lower()
            if query_lower in content_lower:
                # Find the position of the match and extract context
                position = content_lower.find(query_lower)
                
                # Get context (text before and after match)
                context_start = max(0, position - 50)
                context_end = min(len(doc.content), position + len(query) + 50)
                
                # Create context with ellipsis for truncated text
                context = doc.content[context_start:context_end]
                if context_start > 0:
                    context = "..." + context
                if context_end < len(doc.content):
                    context = context + "..."
                    
                results.append(
                    SearchResult(
                        document_id=doc_id,
                        relevance_score=0.8,  # Medium relevance for content matches
                        matched_text=doc.content[position:position + len(query)],
                        context=context,
                        position={"start": position, "end": position + len(query)},
                    )
                )
                
        # Sort by relevance score (descending) and limit to max_results
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        return results[:max_results]
    
    def _semantic_search(
        self, query: str, documents: Dict[str, Document], max_results: int
    ) -> List[SearchResult]:
        """Perform a semantic search on documents with embeddings."""
        # In a real implementation, this would use a vector database or similar
        # For this example, we'll simulate semantic search with a placeholder
        # that returns the same results as local search but with a note
        
        results = self._local_search(query, documents, max_results)
        
        # Add note to context indicating this is a semantic search
        for result in results:
            result.context = "[Semantic Search] " + result.context
            
        return results
    
    def _hybrid_search(
        self, query: str, documents: Dict[str, Document], max_results: int
    ) -> List[SearchResult]:
        """Perform a hybrid search combining keyword and semantic approaches."""
        # In a real implementation, this would combine results from both approaches
        # For this example, we'll combine local and semantic searches
        
        local_results = self._local_search(query, documents, max_results)
        semantic_results = self._semantic_search(query, documents, max_results)
        
        # Combine results (in a real implementation, would deduplicate and rerank)
        combined_results = []
        seen_doc_ids = set()
        
        # Take results from both methods, deduplicating by document_id
        for result in local_results + semantic_results:
            if result.document_id not in seen_doc_ids:
                seen_doc_ids.add(result.document_id)
                combined_results.append(result)
                
                # Add note to context indicating this is a hybrid search
                result.context = "[Hybrid Search] " + result.context
                
                if len(combined_results) >= max_results:
                    break
                    
        return combined_results