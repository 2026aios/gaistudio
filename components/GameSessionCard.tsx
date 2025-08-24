
import React from 'react';
import { GameSession, Member } from '../types';
import { calculateDeadlines, formatDate } from '../utils/date';
import { GUEST_REGISTRATION_PLAYER_THRESHOLD } from '../constants';
import PlayerList from './PlayerList';
import RegistrationControls from './RegistrationControls';

interface GameSessionCardProps {
    session: GameSession;
    members: Member[];
    currentTime: Date;
    onRegisterMember: (memberId: string) => void;
    onRegisterGuest: (guestName: string) => void;
    onCancel: (signupId: string) => void;
}

const GameSessionCard: React.FC<GameSessionCardProps> = ({
    session,
    members,
    currentTime,
    onRegisterMember,
    onRegisterGuest,
    onCancel,
}) => {
    const deadlines = calculateDeadlines(session.date);
    const isRegistrationOpen = currentTime >= deadlines.registrationOpens && currentTime < deadlines.registrationCloses;
    const isGuestRegistrationTime = currentTime >= deadlines.guestRegistrationOpens && currentTime < deadlines.registrationCloses;
    const isGuestSlotAvailable = session.signups.length < GUEST_REGISTRATION_PLAYER_THRESHOLD;
    const canGuestsRegister = isRegistrationOpen && isGuestRegistrationTime && isGuestSlotAvailable;
    const isCancellationAllowed = currentTime < deadlines.cancellationDeadline;

    const getStatusMessage = () => {
        if (currentTime < deadlines.registrationOpens) {
            return `報名將於 ${formatDate(deadlines.registrationOpens)} 開放`;
        }
        if (!isRegistrationOpen && currentTime >= deadlines.registrationCloses) {
            return '本場次報名已截止';
        }
        if (isRegistrationOpen) {
            return `報名開放中，將於 ${formatDate(deadlines.registrationCloses)} 截止`;
        }
        return '';
    };

    return (
        <div className="bg-white dark:bg-gray-800/50 backdrop-blur-sm rounded-2xl shadow-lg p-6 md:p-8 mb-12 border border-gray-200 dark:border-gray-700">
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
                <div>
                    <h2 className="text-2xl font-bold text-blue-600 dark:text-blue-400">即將開打</h2>
                    <p className="text-lg text-gray-600 dark:text-gray-300">{formatDate(session.date)}</p>
                </div>
                <div className="mt-4 md:mt-0 text-right">
                    <p className="text-2xl font-mono font-bold">{session.signups.length} <span className="text-base font-normal text-gray-500 dark:text-gray-400">人已報名</span></p>
                    <p className="text-sm text-yellow-600 dark:text-yellow-400 mt-1">{getStatusMessage()}</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                    <h3 className="text-xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">已報名清單</h3>
                    <PlayerList 
                        signups={session.signups} 
                        onCancel={onCancel} 
                        isCancellationAllowed={isCancellationAllowed} 
                    />
                </div>
                <div>
                    <h3 className="text-xl font-semibold mb-4 border-b pb-2 border-gray-200 dark:border-gray-700">報名區</h3>
                    <RegistrationControls
                        members={members}
                        signups={session.signups}
                        isRegistrationOpen={isRegistrationOpen}
                        canGuestsRegister={canGuestsRegister}
                        onRegisterMember={onRegisterMember}
                        onRegisterGuest={onRegisterGuest}
                    />
                </div>
            </div>
        </div>
    );
};

export default GameSessionCard;
