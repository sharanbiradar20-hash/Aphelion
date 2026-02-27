/**
 * Utility for conditionally joining classNames together.
 * Lightweight replacement for clsx/cn from shadcn's @/lib/utils.
 */
export function cn(...classes) {
    return classes.filter(Boolean).join(' ');
}
