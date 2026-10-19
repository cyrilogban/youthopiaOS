import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getSavedVerses, toggleSavedVerse, type SavedVerse } from '../../services/savedVerses';
import { EmptyState } from '../../components/ui';

export const TheoSaved: React.FC = () => {
  const navigate = useNavigate();
  const [verses, setVerses] = useState<SavedVerse[]>(() => getSavedVerses());

  const remove = (verse: SavedVerse) => {
    const result = toggleSavedVerse(verse);
    setVerses(result.list);
  };

  return (
    <div className="section-stack">
      <section className="page-heading">
        <span className="quiet-chip">Your Scripture library</span>
        <h1>Saved verses.</h1>
        <p>The verses you keep close. Tap Save on any post and it will be kept here.</p>
      </section>

      {verses.length === 0 ? (
        <EmptyState
          title="No saved verses yet"
          body="When something speaks to you, tap Save and it will be kept here."
          action={
            <button className="primary-button" onClick={() => navigate('/theo/home')}>
              Go to home
            </button>
          }
        />
      ) : (
        <div className="section-group">
          {verses.map((verse) => (
            <div key={verse.id} className="post">
              <div className="post-body" style={{ paddingBottom: 4 }}>
                <p className="post-verse" style={{ fontSize: 18 }}>
                  {verse.text}
                </p>
                {verse.reference && <div className="post-ref">{verse.reference}</div>}
              </div>
              <div className="post-actions">
                <button className="post-action" onClick={() => remove(verse)}>
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
