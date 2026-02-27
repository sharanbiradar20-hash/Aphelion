import React from 'react';
import { ArrowRight } from 'lucide-react';
import { cn } from '../../lib/utils';

/**
 * InteractiveHoverButton — Button with expanding background fill + sliding text on hover.
 * Adapted from 21st.dev (Magic UI) for CRA + JSX.
 */
const InteractiveHoverButton = React.forwardRef(
    ({ text = 'Button', className, ...props }, ref) => {
        return (
            <button
                ref={ref}
                className={cn(
                    'group relative cursor-pointer overflow-hidden rounded-full border border-cyan-500/30 bg-slate-900/80 py-2.5 px-8 text-center font-semibold text-slate-200 transition-all duration-300 hover:border-cyan-400/60 hover:shadow-lg hover:shadow-cyan-500/10',
                    className
                )}
                {...props}
            >
                {/* Default text — slides out on hover */}
                <span className="relative z-10 inline-flex items-center gap-2 transition-all duration-300 group-hover:opacity-0 group-hover:-translate-y-6">
                    {text}
                </span>

                {/* Hover text — slides in from below */}
                <span className="absolute inset-0 z-10 flex items-center justify-center gap-2 text-white font-semibold opacity-0 translate-y-6 transition-all duration-300 group-hover:opacity-100 group-hover:translate-y-0">
                    {text}
                    <ArrowRight className="w-4 h-4" />
                </span>

                {/* Background fill — expands from center on hover */}
                <span className="absolute inset-0 z-0 bg-gradient-to-r from-cyan-500 to-blue-500 opacity-0 scale-x-0 transition-all duration-300 ease-out group-hover:opacity-100 group-hover:scale-x-100 origin-center rounded-full"></span>
            </button>
        );
    }
);

InteractiveHoverButton.displayName = 'InteractiveHoverButton';

export { InteractiveHoverButton };
export default InteractiveHoverButton;
