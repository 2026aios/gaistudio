
import React from 'react';
import { Signup } from '../types';

interface PlayerListProps {
    signups: Signup[];
    onCancel: (signupId: string) => void;
    isCancellationAllowed: boolean;
}

const CancelButton: React.FC<{ onClick: () => void, disabled: boolean }> = ({ onClick, disabled }) => (
    <button
        onClick={onClick}
        disabled={disabled}
        className="text-gray-400 hover:text-red-500 dark:hover:text-red-400 disabled:text-gray-600 disabled:cursor-not-allowed transition-colors duration-200"
        aria-label="取消報名"
    >
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
        </svg>
    </button>
);


const PlayerList: React.FC<PlayerListProps> = ({ signups, onCancel, isCancellationAllowed }) => {
    if (signups.length === 0) {
        return <p className="text-gray-500 dark:text-gray-400 italic mt-4">目前尚無人報名</p>;
    }

    return (
        <div className="space-y-3 pr-2 max-h-96 overflow-y-auto">
            {signups.map((signup, index) => (
                <div key={signup.id} className="flex items-center justify-between bg-gray-100 dark:bg-gray-700/50 rounded-lg p-3 animate-fade-in" style={{ animationDelay: `${index * 50}ms` }}>
                    <div className="flex items-center">
                        <span className="font-mono text-sm text-gray-500 dark:text-gray-400 mr-3 w-6 text-center">{index + 1}.</span>
                        <span className="font-medium">{signup.name}</span>
                        {signup.type === 'guest' && <span className="ml-2 text-xs bg-teal-200 text-teal-800 dark:bg-teal-700 dark:text-teal-100 px-2 py-0.5 rounded-full">臨打</span>}
                    </div>
                    <CancelButton onClick={() => onCancel(signup.id)} disabled={!isCancellationAllowed} />
                </div>
            ))}
        </div>
    );
};

export default PlayerList;
