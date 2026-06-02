import { useEffect } from 'react';

const GlobalDragScroll = () => {
    useEffect(() => {
        let isDown = false;
        let startY = 0;
        let startX = 0;
        let scrollTop = 0;
        let scrollLeft = 0;
        let scrollContainer = null;

        const isScrollable = (ele) => {
            // Check if element has scrollable content and is configured to allow scrolling
            const style = window.getComputedStyle(ele);
            const overflowY = style.overflowY;
            const overflowX = style.overflowX;
            
            const isScrollableY = ele.scrollHeight > ele.clientHeight && (overflowY === 'auto' || overflowY === 'scroll');
            const isScrollableX = ele.scrollWidth > ele.clientWidth && (overflowX === 'auto' || overflowX === 'scroll');
            
            return isScrollableY || isScrollableX;
        };

        const getScrollableParent = (node) => {
            if (node == null || node === document.body || node === document.documentElement) {
                return null;
            }
            if (isScrollable(node)) {
                return node;
            }
            return getScrollableParent(node.parentNode);
        };

        const mouseDownHandler = function (e) {
            scrollContainer = getScrollableParent(e.target);
            if (!scrollContainer) return;
            
            isDown = true;
            // Support both mouse and touch events
            startY = e.type === 'touchstart' ? e.touches[0].clientY : e.clientY;
            startX = e.type === 'touchstart' ? e.touches[0].clientX : e.clientX;
            scrollTop = scrollContainer.scrollTop;
            scrollLeft = scrollContainer.scrollLeft;
            scrollContainer.style.cursor = 'grabbing';
        };

        const mouseMoveHandler = function (e) {
            if (!isDown || !scrollContainer) return;
            
            // Allow default behavior for elements like range inputs
            if (e.target.tagName === 'INPUT' && e.target.type === 'range') return;
            
            e.preventDefault(); // Prevents default drag-to-highlight
            const currentY = e.type === 'touchmove' ? e.touches[0].clientY : e.clientY;
            const currentX = e.type === 'touchmove' ? e.touches[0].clientX : e.clientX;
            const dy = currentY - startY;
            const dx = currentX - startX;
            scrollContainer.scrollTop = scrollTop - dy;
            scrollContainer.scrollLeft = scrollLeft - dx;
        };

        const mouseUpHandler = function () {
            if (scrollContainer) {
                scrollContainer.style.cursor = '';
            }
            isDown = false;
            scrollContainer = null;
        };

        // Mouse events
        window.addEventListener('mousedown', mouseDownHandler);
        window.addEventListener('mousemove', mouseMoveHandler, { passive: false });
        window.addEventListener('mouseup', mouseUpHandler);
        
        // Touch events
        window.addEventListener('touchstart', mouseDownHandler, { passive: false });
        window.addEventListener('touchmove', mouseMoveHandler, { passive: false });
        window.addEventListener('touchend', mouseUpHandler);

        return () => {
            window.removeEventListener('mousedown', mouseDownHandler);
            window.removeEventListener('mousemove', mouseMoveHandler);
            window.removeEventListener('mouseup', mouseUpHandler);
            window.removeEventListener('touchstart', mouseDownHandler);
            window.removeEventListener('touchmove', mouseMoveHandler);
            window.removeEventListener('touchend', mouseUpHandler);
        };
    }, []);

    return null;
};

export default GlobalDragScroll;
