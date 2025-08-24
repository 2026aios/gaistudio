
import React from 'react';
import { Member } from '../types';
import { QUARTERLY_FEE_BASE, QUARTERLY_FEE_THRESHOLD, QUARTERLY_FEE_PER_GAME_EXTRA } from '../constants';

interface MemberStatsProps {
    members: Member[];
}

const calculateFee = (quarterlyAttendance: number): number => {
    if (quarterlyAttendance <= QUARTERLY_FEE_THRESHOLD) {
        return QUARTERLY_FEE_BASE;
    }
    const extraGames = quarterlyAttendance - QUARTERLY_FEE_THRESHOLD;
    return QUARTERLY_FEE_BASE + (extraGames * QUARTERLY_FEE_PER_GAME_EXTRA);
};

const MemberStats: React.FC<MemberStatsProps> = ({ members }) => {
    return (
        <div className="mt-12">
            <h2 className="text-2xl font-bold text-center mb-6">會員統計資料</h2>
            <div className="overflow-x-auto bg-white dark:bg-gray-800/50 rounded-xl shadow-md border border-gray-200 dark:border-gray-700">
                <table className="w-full min-w-max text-left">
                    <thead className="border-b border-gray-200 dark:border-gray-700">
                        <tr>
                            <th className="p-4 font-semibold">會員姓名</th>
                            <th className="p-4 font-semibold text-center">本月次數</th>
                            <th className="p-4 font-semibold text-center">本季次數</th>
                            <th className="p-4 font-semibold text-right">本季費用 (NTD)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {members.sort((a,b) => a.name.localeCompare(b.name)).map((member, index) => (
                            <tr key={member.id} className={`border-t border-gray-200 dark:border-gray-700 ${index % 2 === 0 ? '' : 'bg-gray-50/50 dark:bg-gray-800/50'}`}>
                                <td className="p-4 font-medium">{member.name}</td>
                                <td className="p-4 text-center font-mono">{member.monthlyAttendance}</td>
                                <td className="p-4 text-center font-mono">{member.quarterlyAttendance}</td>
                                <td className="p-4 text-right font-mono font-bold text-blue-600 dark:text-blue-400">
                                    {calculateFee(member.quarterlyAttendance).toLocaleString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default MemberStats;
