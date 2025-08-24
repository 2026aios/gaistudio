import React, { useState } from 'react';
import { Member, Signup } from '../types';

interface RegistrationControlsProps {
    members: Member[];
    signups: Signup[];
    isRegistrationOpen: boolean;
    canGuestsRegister: boolean;
    onRegisterMember: (memberId: string) => void;
    onRegisterGuest: (guestName: string) => void;
}

const GuestRegistrationForm: React.FC<{ onRegisterGuest: (name: string) => void }> = ({ onRegisterGuest }) => {
    const [guestName, setGuestName] = useState('');

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (guestName.trim()) {
            onRegisterGuest(guestName.trim());
            setGuestName('');
        }
    };

    return (
        <div className="mt-4 border-t border-gray-200 dark:border-gray-700 pt-4">
             <p className="text-sm font-semibold mb-2 text-green-600 dark:text-green-400">臨打已開放</p>
            <form onSubmit={handleSubmit} className="flex space-x-2">
                <input
                    type="text"
                    value={guestName}
                    onChange={(e) => setGuestName(e.target.value)}
                    placeholder="輸入姓名"
                    className="flex-grow bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 dark:text-gray-200"
                />
                <button type="submit" className="bg-green-500 text-white font-semibold px-4 py-2 rounded-md hover:bg-green-600 transition-colors duration-200">
                    報名
                </button>
            </form>
        </div>
    );
};

const RegistrationControls: React.FC<RegistrationControlsProps> = ({
    members,
    signups,
    isRegistrationOpen,
    canGuestsRegister,
    onRegisterMember,
    onRegisterGuest
}) => {
    if (!isRegistrationOpen) {
        return <p className="text-gray-500 dark:text-gray-400 italic mt-4">報名尚未開放或已截止</p>;
    }
    
    const signedUpMemberIds = new Set(signups.filter(s => s.type === 'member').map(s => s.id));
    const availableMembers = members.filter(m => !signedUpMemberIds.has(m.id));

    return (
        <div>
            <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">會員報名</h4>
            <div className="max-h-80 overflow-y-auto pr-2">
                {availableMembers.length > 0 ? (
                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                        {availableMembers
                            .sort((a, b) => parseInt(a.id.slice(1)) - parseInt(b.id.slice(1)))
                            .map(member => (
                            <button
                                key={member.id}
                                onClick={() => onRegisterMember(member.id)}
                                className="flex flex-col items-center justify-center text-center bg-white dark:bg-gray-700/50 p-2 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/50 transition-colors duration-200 shadow-sm border border-gray-200 dark:border-gray-700 h-20"
                            >
                                <span className="text-xs text-gray-500 dark:text-gray-400">{parseInt(member.id.replace('m',''))}</span>
                                <span className="font-medium text-base mt-1">{member.name}</span>
                            </button>
                        ))}
                    </div>
                ) : (
                    <p className="text-gray-500 dark:text-gray-400 text-sm mt-2">所有會員皆已報名</p>
                )}
            </div>

            {canGuestsRegister && <GuestRegistrationForm onRegisterGuest={onRegisterGuest} />}
            {!canGuestsRegister && isRegistrationOpen && (
                 <div className="mt-4 border-t border-gray-200 dark:border-gray-700 pt-4">
                    <p className="text-sm text-gray-500 dark:text-gray-400">臨打報名條件尚未滿足（前一晚 8:00 後且總人數少於 17 人）。</p>
                 </div>
            )}
        </div>
    );
};

export default RegistrationControls;