import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Member, GameSession, Signup, Theme } from './types';
import { INITIAL_MEMBERS, GAME_DAYS_OF_WEEK, GUEST_REGISTRATION_PLAYER_THRESHOLD } from './constants';
import { getUpcomingGameDates, calculateDeadlines } from './utils/date';
import Header from './components/Header';
import GameSessionCard from './components/GameSessionCard';
import MemberStats from './components/MemberStats';

const App: React.FC = () => {
    const [currentTime, setCurrentTime] = useState(new Date());
    const [theme, setTheme] = useState<Theme>(Theme.Light);
    const [members, setMembers] = useState<Member[]>(() => {
        const savedMembers = localStorage.getItem('badmintonMembers');
        return savedMembers ? JSON.parse(savedMembers) : INITIAL_MEMBERS;
    });

    const [gameSessions, setGameSessions] = useState<GameSession[]>([]);

    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    useEffect(() => {
        const hour = currentTime.getHours();
        setTheme(hour >= 6 && hour < 18 ? Theme.Light : Theme.Dark);
    }, [currentTime]);

    useEffect(() => {
        const initializeOrUpdateSessions = () => {
            const savedSessionsData = localStorage.getItem('badmintonGameSessions');
            const savedSessionsMap = new Map<string, GameSession>();
            if (savedSessionsData) {
                try {
                    const parsedSessions = JSON.parse(savedSessionsData);
                    if (Array.isArray(parsedSessions)) {
                        parsedSessions.forEach((s: any) => {
                             if (s.id && s.date) {
                                savedSessionsMap.set(s.id, { ...s, date: new Date(s.date) });
                            }
                        });
                    }
                } catch (e) {
                    console.error("Failed to parse game sessions from localStorage", e);
                }
            }

            const upcomingGameDates = getUpcomingGameDates(GAME_DAYS_OF_WEEK);
            const now = new Date();

            const newSessions = upcomingGameDates.map(date => {
                const dateString = date.toISOString().split('T')[0];
                const id = `session-${dateString}`;
                const existingSession = savedSessionsMap.get(id);
                const { cancellationDeadline } = calculateDeadlines(date);

                if (now > cancellationDeadline) {
                    return { id, date, signups: [] };
                }

                return existingSession || { id, date, signups: [] };
            });

            setGameSessions(prevSessions => {
                if (JSON.stringify(prevSessions) !== JSON.stringify(newSessions)) {
                    return newSessions;
                }
                return prevSessions;
            });
        };

        initializeOrUpdateSessions();
        const interval = setInterval(initializeOrUpdateSessions, 30000); // Check for updates every 30 seconds
        return () => clearInterval(interval);
    }, []);

    useEffect(() => {
        localStorage.setItem('badmintonMembers', JSON.stringify(members));
        if (gameSessions.length > 0) {
            localStorage.setItem('badmintonGameSessions', JSON.stringify(gameSessions));
        }
    }, [members, gameSessions]);


    const handleRegisterMember = useCallback((memberId: string, sessionId: string) => {
        setGameSessions(prev =>
            prev.map(session => {
                if (session.id === sessionId) {
                    if (session.signups.some(s => s.id === memberId)) return session;
                    const member = members.find(m => m.id === memberId);
                    if (!member) return session;

                    const newSignup: Signup = {
                        id: member.id, name: member.name, type: 'member', timestamp: new Date(),
                    };
                    const updatedSignups = [...session.signups, newSignup].sort((a, b) => a.name.localeCompare(b.name));
                    return { ...session, signups: updatedSignups };
                }
                return session;
            })
        );

        setMembers(prev => prev.map(m => {
            if (m.id === memberId) {
                return {
                    ...m,
                    monthlyAttendance: m.monthlyAttendance + 1,
                    quarterlyAttendance: m.quarterlyAttendance + 1,
                };
            }
            return m;
        }));
    }, [members]);

    const handleRegisterGuest = useCallback((guestName: string, sessionId: string) => {
        setGameSessions(prev =>
            prev.map(session => {
                if (session.id === sessionId && session.signups.length < GUEST_REGISTRATION_PLAYER_THRESHOLD) {
                    const newSignup: Signup = {
                        id: `guest-${Date.now()}`, name: guestName, type: 'guest', timestamp: new Date(),
                    };
                    const updatedSignups = [...session.signups, newSignup].sort((a, b) => a.name.localeCompare(b.name));
                    return { ...session, signups: updatedSignups };
                }
                return session;
            })
        );
    }, []);

    const handleCancel = useCallback((signupId: string, sessionId: string) => {
        const sessionToUpdate = gameSessions.find(s => s.id === sessionId);
        if (!sessionToUpdate) return;
        const signupToRemove = sessionToUpdate.signups.find(s => s.id === signupId);
        if (!signupToRemove) return;

        setGameSessions(prev =>
            prev.map(s =>
                s.id === sessionId
                    ? { ...s, signups: s.signups.filter(signup => signup.id !== signupId) }
                    : s
            )
        );

        if (signupToRemove.type === 'member') {
            setMembers(prev => prev.map(m => {
                if (m.id === signupToRemove.id) {
                    return {
                        ...m,
                        monthlyAttendance: Math.max(0, m.monthlyAttendance - 1),
                        quarterlyAttendance: Math.max(0, m.quarterlyAttendance - 1),
                    };
                }
                return m;
            }));
        }
    }, [gameSessions]);
    
    const nextSession = useMemo(() => {
        return gameSessions
            .filter(s => currentTime < calculateDeadlines(s.date).registrationCloses)
            .sort((a, b) => a.date.getTime() - b.date.getTime())[0];
    }, [gameSessions, currentTime]);
    
    const handleRegisterMemberForSession = useCallback((memberId: string) => {
        if (nextSession) handleRegisterMember(memberId, nextSession.id);
    }, [nextSession, handleRegisterMember]);

    const handleRegisterGuestForSession = useCallback((guestName: string) => {
        if (nextSession) handleRegisterGuest(guestName, nextSession.id);
    }, [nextSession, handleRegisterGuest]);

    const handleCancelForSession = useCallback((signupId: string) => {
        if (nextSession) handleCancel(signupId, nextSession.id);
    }, [nextSession, handleCancel]);


    return (
        <div className={`${theme === Theme.Dark ? 'dark' : ''} transition-colors duration-500`}>
            <div className="min-h-screen bg-gray-50 dark:bg-gray-900 text-gray-800 dark:text-gray-200 font-sans">
                <main className="container mx-auto px-4 py-8 md:py-16">
                    <Header />
                    {nextSession ? (
                        <GameSessionCard
                            session={nextSession}
                            members={members}
                            currentTime={currentTime}
                            onRegisterMember={handleRegisterMemberForSession}
                            onRegisterGuest={handleRegisterGuestForSession}
                            onCancel={handleCancelForSession}
                        />
                    ) : (
                         <div className="text-center p-8 bg-white dark:bg-gray-800/50 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
                            <h2 className="text-2xl font-bold text-gray-700 dark:text-gray-300">暫無即將開打的球局</h2>
                            <p className="mt-2 text-gray-500 dark:text-gray-400">系統正在準備下週的場次，請稍後再回來查看。</p>
                        </div>
                    )}
                    <MemberStats members={members} />
                </main>
            </div>
        </div>
    );
};

export default App;