# pages/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta, date
import json
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
import re
from .models import ProfileImage
from django.views.decorators.csrf import csrf_exempt 

# Import your models
from .models import (
    Profile, Message, Thread, Like, Block, PrivateAccessRequest, 
    HotDate, HotDateView, HotDateNotification, Blog, UserActivity
)

# ======================
# PREVIEW USE - START (NEW VIEWS)
# ======================

def join_view(request):
    """Handle new user signups - redirect to preview gate"""
    if request.method == 'POST':
        # Your existing signup logic here
        # After successful signup:
        return redirect('preview_gate')
    return render(request, 'signup.html')

def preview_gate(request):
    """Preview gate homepage for unapproved users"""
    if request.user.is_authenticated:
        try:
            user_profile = Profile.objects.get(user=request.user)
            if user_profile.is_approved or request.user.is_staff:
                return redirect('dashboard')  # Skip gate if already approved or staff
        except Profile.DoesNotExist:
            pass
    
    return render(request, 'pages/preview_gate.html')

@login_required
def browse_preview(request):
    """Preview browsing for unapproved users"""
    try:
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.is_approved or request.user.is_staff:
            return redirect('dashboard')  # Redirect to full dashboard if approved or staff
    except Profile.DoesNotExist:
        pass
    
    # Show limited profiles for preview
    profiles = Profile.objects.filter(
        is_approved=True
    ).exclude(
        Q(user=request.user) |
        Q(user__in=Block.objects.filter(blocker=request.user).values('blocked')) |
        Q(user__in=Block.objects.filter(blocked=request.user).values('blocker'))
    ).order_by('-created_at')
    
    paginator = Paginator(profiles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'is_approved_user': False,
        'suggested_profiles': page_obj,
        'search_query': None,
        'search_performed': False,
    }
    return render(request, 'pages/preview_gr8date_dashboard_fixed_v10_nolines.html', context)

# ======================
# PREVIEW USE - END
# ======================

# Core Pages
def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'pages/home.html')

@login_required
def dashboard(request):
    # ======================
    # PREVIEW USE - START (ADD APPROVAL CHECK)
    # ======================
    try:
        user_profile = Profile.objects.get(user=request.user)
        is_approved_user = user_profile.is_approved
    except Profile.DoesNotExist:
        is_approved_user = False
    
    # FIX: If user is not approved AND not staff/superuser, redirect to preview gate
    if not is_approved_user and not request.user.is_staff:
        return redirect('preview_gate')
    # ======================
    # PREVIEW USE - END
    # ======================
    
    # Start with base queryset
    suggested_profiles = Profile.objects.filter(
        is_approved=True
    ).exclude(
        Q(user=request.user) |
        Q(user__in=Block.objects.filter(blocker=request.user).values('blocked')) |
        Q(user__in=Block.objects.filter(blocked=request.user).values('blocker'))
    )
    
    # Check if we have a search query from session
    search_query = request.session.pop('search_query', None)
    search_performed = request.session.pop('search_performed', False)
    
    if search_query and search_performed:
        # Apply search filtering
        age_range_match = re.match(r'(\d+)-(\d+)', search_query)
        if age_range_match:
            min_age = int(age_range_match.group(1))
            max_age = int(age_range_match.group(2))
            
            if min_age > max_age:
                min_age, max_age = max_age, min_age
            
            today = date.today()
            max_birth_date = today.replace(year=today.year - min_age)
            min_birth_date = today.replace(year=today.year - max_age - 1)
            
            suggested_profiles = suggested_profiles.filter(
                date_of_birth__gte=min_birth_date,
                date_of_birth__lte=max_birth_date
            )
        
        elif search_query.isdigit():
            age = int(search_query)
            today = date.today()
            min_birth_date = today.replace(year=today.year - age - 1)
            max_birth_date = today.replace(year=today.year - age + 1)
            
            suggested_profiles = suggested_profiles.filter(
                date_of_birth__gte=min_birth_date,
                date_of_birth__lte=max_birth_date
            )
        
        else:
            search_conditions = Q()
            search_conditions |= Q(user__username__icontains=search_query)
            search_conditions |= Q(user__first_name__icontains=search_query)
            search_conditions |= Q(user__last_name__icontains=search_query)
            search_conditions |= Q(headline__icontains=search_query)
            search_conditions |= Q(about__icontains=search_query)
            search_conditions |= Q(location__icontains=search_query)
            search_conditions |= Q(my_interests__icontains=search_query)
            search_conditions |= Q(must_have_tags__icontains=search_query)
            search_conditions |= Q(pets__icontains=search_query)
            search_conditions |= Q(diet__icontains=search_query)
            
            suggested_profiles = suggested_profiles.filter(search_conditions)
    
    # Order and paginate
    suggested_profiles = suggested_profiles.order_by('-created_at')
    paginator = Paginator(suggested_profiles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'profile': user_profile,
        'suggested_profiles': page_obj,
        'search_query': search_query,
        'search_performed': search_performed,
        # ======================
        # PREVIEW USE - START (ADD TO CONTEXT)
        # ======================
        'is_approved_user': is_approved_user,
        # ======================
        # PREVIEW USE - END
        # ======================
    }
    return render(request, 'pages/gr8date_dashboard_fixed_v10_nolines.html', context)

@login_required
def search(request):
    """ENHANCED search - redirect to dashboard with filtered results"""
    query = request.GET.get('q', '').strip()
    
    if not query:
        return redirect('dashboard')
    
    # Store search query in session for dashboard to use
    request.session['search_query'] = query
    request.session['search_performed'] = True
    
    return redirect('dashboard')

# Profile Management
@login_required
def profile_view(request):
    profile = Profile.objects.get(user=request.user)
    context = {'profile': profile}
    return render(request, 'pages/profile_view.html', context)

@login_required
def profile_edit(request):
    profile = Profile.objects.get(user=request.user)
     
    if request.method == 'POST':
        # Your existing profile edit logic
        profile.headline = request.POST.get('headline', '')
        profile.about = request.POST.get('about', '')
        profile.location = request.POST.get('location', '')
        profile.my_gender = request.POST.get('my_gender', '')
        profile.looking_for = request.POST.get('looking_for', '')
        profile.my_interests = request.POST.get('my_interests', '')
        profile.children = request.POST.get('children', '')
        profile.preferred_age_min = request.POST.get('preferred_age_min', 18)
        profile.preferred_age_max = request.POST.get('preferred_age_max', 99)
        profile.preferred_intent = request.POST.get('preferred_intent', '')
        profile.preferred_distance = request.POST.get('preferred_distance', '')
        profile.save()  
    
        return redirect('profile_view')
        
    context = {
        'me': profile,
        'ages': range(18, 81),
    }
    return render(request, 'pages/profile_edit.html', context)

@login_required
def profile_detail(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    is_own_profile = request.user == profile.user
    
    # Check if requester has active access to private photos
    has_private_access = False
    access_request = None
    has_pending_request = False
    
    if not is_own_profile and request.user.is_authenticated:
        access_request = PrivateAccessRequest.objects.filter(
            requester=request.user,
            target_user=profile.user
        ).first()
        
        if access_request:
            if access_request.status == 'approved':
                has_private_access = True
            elif access_request.status == 'pending':
                has_pending_request = True
    
    # Get images
    public_images = profile.images.filter(is_private=False)
    private_images = profile.images.filter(is_private=True)
    
    # Your existing context variables
    is_liked = Like.objects.filter(
        liker=request.user, 
        liked_user=profile.user
    ).exists()
    
    is_blocked = Block.objects.filter(
        blocker=request.user,
        blocked=profile.user
    ).exists()
    
    # Get next/previous profiles for navigation
    all_profiles = Profile.objects.filter(is_approved=True).exclude(user=request.user)
    current_index = list(all_profiles).index(profile) if profile in list(all_profiles) else -1
    
    previous_profile_id = None
    next_profile_id = None
    
    if current_index > 0:
        previous_profile_id = all_profiles[current_index - 1].user_id
    if current_index < len(all_profiles) - 1:
        next_profile_id = all_profiles[current_index + 1].user_id
    
    context = {
        'profile': profile,
        'public_images': public_images,
        'private_images': private_images,
        'is_own_profile': is_own_profile,
        'has_private_access': has_private_access,
        'has_pending_request': has_pending_request,
        'access_request': access_request,
        'is_liked': is_liked,
        'is_blocked': is_blocked,
        'previous_profile_id': previous_profile_id,
        'next_profile_id': next_profile_id,
    }
    return render(request, 'pages/profile_view.html', context)

@login_required
@csrf_exempt
def upload_profile_image(request):
    if request.method == 'POST' and request.FILES.get('image'):
        try:
            image_file = request.FILES['image']
            is_private = request.POST.get('is_private') == 'true'
            
            # Validate file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse({
                    'success': False, 
                    'error': 'Invalid file type. Please upload JPEG, PNG, GIF, or WebP.'
                }, status=400)
            
            # Validate file size (max 5MB)
            if image_file.size > 5 * 1024 * 1024:
                return JsonResponse({
                    'success': False,
                    'error': 'File too large. Maximum size is 5MB.'
                }, status=400)
            
            # Get or create user profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            # Create new ProfileImage
            profile_image = ProfileImage.objects.create(
                profile=profile,
                image=image_file,
                is_private=is_private
            )
            
            return JsonResponse({
                'success': True, 
                'image_id': profile_image.id,
                'image_url': profile_image.image.url
            })
            
        except Exception as e:
            print(f"DEBUG: Error uploading image: {e}")
            return JsonResponse({
                'success': False, 
                'error': f'Upload failed: {str(e)}'
            }, status=500)
    
    return JsonResponse({
        'success': False, 
        'error': 'No image file provided'
    }, status=400)

@login_required
def delete_image(request, image_id):
    try:
        image = ProfileImage.objects.get(id=image_id, profile=request.user.profile)
        image.delete()
        return JsonResponse({'success': True})
    except ProfileImage.DoesNotExist:
        return JsonResponse({'success': False}, status=404)

# Likes & Matching - UPDATED FOR CONSISTENT JSON RESPONSES
@login_required
def like_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        like, created = Like.objects.get_or_create(
            liker=request.user,
            liked_user=target_user
        )
        
        if not created:
            like.delete()
            return JsonResponse({'status': 'success', 'action': 'unliked'})
        
        # Check if it's a match (target user also liked current user)
        is_match = Like.objects.filter(
            liker=target_user,
            liked_user=request.user
        ).exists()
        
        return JsonResponse({
            'status': 'success', 
            'action': 'liked',
            'is_match': is_match
        })
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def unfavorite_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        Like.objects.filter(
            liker=request.user,
            liked_user=target_user
        ).delete()
        
        return JsonResponse({'status': 'success', 'action': 'unliked'})
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def likes_received(request):
    likes = Like.objects.filter(
        liked_user=request.user
    ).select_related('liker', 'liker__profile')
    
    context = {'likes': likes}
    return render(request, 'pages/likes_received.html', context)

@login_required
def likes_given(request):
    likes = Like.objects.filter(
        liker=request.user
    ).select_related('liked_user', 'liked_user__profile')
    
    context = {'likes': likes}
    return render(request, 'pages/likes_given.html', context)

@login_required
def matches_list(request):
    # Get all likes given by current user
    likes_given = Like.objects.filter(
        liker=request.user
    ).select_related('liked_user', 'liked_user__profile')
    
    # Get all likes received by current user  
    likes_received = Like.objects.filter(
        liked_user=request.user
    ).select_related('liker', 'liker__profile')
    
    # Get all blocked users
    blocked_users = Block.objects.filter(
        blocker=request.user
    ).select_related('blocked', 'blocked__profile')
    
    context = {
        'likes_given': likes_given,
        'likes_received': likes_received, 
        'blocked_users': blocked_users
    }
    return render(request, 'pages/matches_list.html', context)

# Messaging
@login_required
def messages_combined(request):
    threads = Thread.objects.filter(
        Q(user_a=request.user) | Q(user_b=request.user)
    ).prefetch_related('messages').order_by('-updated_at')

    # Create thread data with other_user information
    thread_data = []
    for thread in threads:
        other_user = thread.get_other_user(request.user)
        unread_count = thread.messages.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        thread_data.append({
            'thread': thread,
            'other_user': other_user,
            'unread_count': unread_count,
            'last_message': thread.last_message,
            'updated_at': thread.updated_at
        })

    # Mark threads as read when user views them
    for thread in threads:
        thread.messages.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

    # Get access requests for the current user
    pending_requests_received = PrivateAccessRequest.objects.filter(
        target_user=request.user,
        status='pending'
    )

    context = {
        'threads': thread_data,
        'pending_requests_received': pending_requests_received
    }
    return render(request, 'pages/messages_combined.html', context)

@login_required
def message_thread(request, user_id):
    other_user = get_object_or_404(User, id=user_id)
    
    # Get or create thread
    thread = Thread.get_or_create_for(request.user, other_user)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            message = Message.objects.create(
                thread=thread,
                sender=request.user,
                recipient=other_user,
                text=text
            )
            
            # Update thread timestamp
            thread.save()
            
            # Return message data for AJAX handling
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message_id': message.id,
                    'text': message.text,
                    'created_at': message.created_at.strftime('%b %d, %Y %H:%M'),
                    'sender_id': message.sender_id
                })
            else:
                # Fallback for non-AJAX requests
                return redirect('message_thread', user_id=user_id)
        
        return JsonResponse({'success': False, 'error': 'Empty message'})
    
    # GET request - show the thread
    messages = thread.messages.all().order_by('created_at')
    
    context = {
        'thread': thread,
        'other_user': other_user,
        'messages': messages,
    }
    return render(request, 'pages/message_thread.html', context)

@login_required
def delete_conversation(request, thread_id):
    if request.method == 'POST':
        thread = get_object_or_404(Thread, id=thread_id)
        
        # Verify user is part of the thread
        if request.user not in [thread.user_a, thread.user_b]:
            return JsonResponse({'ok': False, 'error': 'Not authorized'})
        
        # Delete all messages in the thread
        thread.messages.all().delete()
        
        return JsonResponse({'ok': True})
    
    return JsonResponse({'ok': False, 'error': 'Invalid method'})

@login_required
def messages_unread_count(request):
    """Return count of unread messages for the current user - WITH DEBUGGING"""
    try:
        count = Message.objects.filter(
            recipient=request.user,
            is_read=False
        ).count()
        
        print(f"DEBUG: Messages badge count for {request.user}: {count}")
        
        return JsonResponse({'count': count})
    except Exception as e:
        print(f"DEBUG: Error in messages_unread_count: {e}")
        return JsonResponse({'count': 0})

# Private Photo Access Views
@login_required
def request_private_access(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        # Don't allow requesting access to yourself
        if request.user == target_user:
            return JsonResponse({'status': 'error', 'message': 'Cannot request access to your own photos'})
        
        # Check if already exists
        existing_request = PrivateAccessRequest.objects.filter(
            requester=request.user,
            target_user=target_user
        ).first()
        
        if existing_request:
            if existing_request.status == 'pending':
                return JsonResponse({'status': 'pending', 'message': 'Request already pending'})
            elif existing_request.status == 'approved':
                return JsonResponse({'status': 'already_approved', 'message': 'You already have access'})
        
        # Create new request
        access_request = PrivateAccessRequest.objects.create(
            requester=request.user,
            target_user=target_user
        )
        
        # Send notification message to target user
        message_text = f"🔒 {request.user.username} requested access to your private photos. Go to your pending requests to approve or deny."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, target_user),
            sender=request.user,
            recipient=target_user,
            text=message_text
        )
        
        return JsonResponse({'status': 'request_sent', 'message': 'Access request sent!'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

@login_required
def approve_private_access(request, request_id):
    access_request = get_object_or_404(PrivateAccessRequest, id=request_id, target_user=request.user)
    
    if access_request.status == 'pending':
        access_request.status = 'approved'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.save()
        
        # Send approval message with 72-hour notice
        approval_message = f"✅ {request.user.username} approved your private photo access request! You can now view their private photos for 72 hours."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, access_request.requester),
            sender=request.user,
            recipient=access_request.requester,
            text=approval_message
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'approved', 'message': 'Access granted for 72 hours!'})
        else:
            return redirect('messages_list')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def deny_private_access(request, request_id):
    access_request = get_object_or_404(PrivateAccessRequest, id=request_id, target_user=request.user)
    
    if access_request.status == 'pending':
        access_request.status = 'denied'
        access_request.reviewed_by = request.user
        access_request.reviewed_at = timezone.now()
        access_request.save()
        
        # Send denial message
        denial_message = f"❌ {request.user.username} denied your private photo access request."
        Message.objects.create(
            thread=Thread.get_or_create_for(request.user, access_request.requester),
            sender=request.user,
            recipient=access_request.requester,
            text=denial_message
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'denied', 'message': 'Access denied'})
        else:
            return redirect('messages_list')
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def pending_requests(request):
    # Get pending requests for the current user
    pending_requests = PrivateAccessRequest.objects.filter(
        target_user=request.user,
        status='pending'
    ).select_related('requester', 'requester__profile')
    
    context = {
        'pending_requests': pending_requests
    }
    return render(request, 'pages/pending_requests.html', context)

# Blog
def blog_list(request):
    posts = Blog.objects.filter(
        status=Blog.Status.PUBLISHED,
        published_at__lte=timezone.now()
    ).order_by('-published_at')
    
    context = {'posts': posts}
    return render(request, 'pages/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(Blog, slug=slug, status=Blog.Status.PUBLISHED)
    context = {'post': post}
    return render(request, 'pages/blog_detail.html', context)

# Admin Approval System
@login_required
def admin_profile_approvals(request):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    pending_profiles = Profile.objects.filter(is_approved=False)
    context = {'pending_profiles': pending_profiles}
    return render(request, 'pages/admin_approvals.html', context)

@login_required
def admin_approve_profile(request, profile_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    profile = get_object_or_404(Profile, id=profile_id)
    profile.is_approved = True
    profile.save()
    
    return redirect('admin_profile_approvals')

@login_required
def admin_reject_profile(request, profile_id):
    if not request.user.is_staff:
        return redirect('dashboard')
    
    profile = get_object_or_404(Profile, id=profile_id)
    # You might want to add a reason field or delete the profile
    profile.delete()
    
    return redirect('admin_profile_approvals')

# Blocking - UPDATED FOR JSON RESPONSES
@login_required
def block_user(request, user_id):
    if request.method == 'POST':
        target_user = get_object_or_404(User, id=user_id)
        
        Block.objects.get_or_create(
            blocker=request.user,
            blocked=target_user
        )
        
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success'})
        return redirect('profile_detail', user_id=user_id)
    
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def unblock_user(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    
    Block.objects.filter(
        blocker=request.user,
        blocked=target_user
    ).delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})
    return redirect('profile_detail', user_id=user_id)

# HotDates - ENHANCED WITH CANCELLATION AND NOTIFICATIONS
@login_required
def hotdates_new_count(request):
    """Count new Hot Dates AND cancellation notifications for the current user - WITH DEBUGGING"""
    try:
        # Get Hot Dates created in the last 24 hours that the user hasn't viewed
        cutoff_time = timezone.now() - timedelta(hours=24)
        
        # Get Hot Dates created recently that user hasn't viewed
        new_hotdates_count = HotDate.objects.filter(
            created_at__gte=cutoff_time,
            is_active=True,
            is_cancelled=False
        ).exclude(
            views__user=request.user
        ).count()
        
        # Get unread cancellation notifications
        cancellation_notifications_count = HotDateNotification.objects.filter(
            user=request.user,
            is_read=False,
            notification_type='cancelled'
        ).count()
        
        total_count = new_hotdates_count + cancellation_notifications_count
        
        print(f"DEBUG: Hot Dates badge count for {request.user}: {total_count} "
              f"(new: {new_hotdates_count}, cancellations: {cancellation_notifications_count})")
        
        return JsonResponse({
            'count': total_count,
            'preview': getattr(request, 'preview_mode', False)
        })
        
    except Exception as e:
        print(f"DEBUG: Error in hotdates_new_count: {e}")
        return JsonResponse({
            'count': 0,
            'preview': getattr(request, 'preview_mode', False)
        })

@login_required
def hotdate_list(request):
    """Display list of Hot Dates with cancellation status"""
    hot_dates = HotDate.objects.filter(
        is_active=True,
        date_time__gte=timezone.now()
    ).order_by('date_time')
    
    # Get which Hot Dates the user has already viewed
    viewed_hotdates = HotDateView.objects.filter(
        user=request.user
    ).values_list('hot_date_id', flat=True)
    
    # Mark cancellation notifications as read when user views the list
    HotDateNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    return render(request, 'pages/hotdate_list.html', {
        'hot_dates': hot_dates,
        'viewed_hotdates': viewed_hotdates
    })

@login_required
def hotdate_create(request):
    """Display and handle Hot Date creation form"""
    if request.method == 'POST':
        try:
            # Get form data
            activity = request.POST.get('activity')
            vibe = request.POST.get('vibe')
            budget = request.POST.get('budget')
            duration = request.POST.get('duration')
            date = request.POST.get('date')
            time = request.POST.get('time')
            area = request.POST.get('area')
            group_size = request.POST.get('group_size')
            audience = request.POST.get('audience')
            
            # Combine date and time
            from datetime import datetime
            date_time = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            date_time = timezone.make_aware(date_time)
            
            # Create Hot Date
            hot_date = HotDate.objects.create(
                host=request.user,
                activity=activity,
                vibe=vibe,
                budget=budget,
                duration=duration,
                date_time=date_time,
                area=area,
                group_size=group_size,
                audience=audience
            )
            
            # Add success message
            messages.success(request, 'Your Hot Date has been created successfully! 🔥')
            
            # Redirect to Hot Dates list
            return redirect('hotdate_list')
            
        except Exception as e:
            messages.error(request, f'Error creating Hot Date: {str(e)}')
    
    # If GET request or form has errors, show the form
    return render(request, 'pages/hotdate_create.html')

@login_required
def hotdate_mark_seen(request, hotdate_id):
    """Mark a Hot Date as seen by the user"""
    try:
        hot_date = HotDate.objects.get(id=hotdate_id)
        HotDateView.objects.get_or_create(
            user=request.user,
            hot_date=hot_date
        )
        return JsonResponse({'success': True})
    except HotDate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Hot Date not found'})

@login_required
def hotdate_cancel(request, hotdate_id):
    """Cancel a Hot Date and send notifications to interested users"""
    try:
        hot_date = HotDate.objects.get(id=hotdate_id, host=request.user)
        
        # Mark as cancelled
        hot_date.is_cancelled = True
        hot_date.cancelled_at = timezone.now()
        hot_date.save()
        
        # Send cancellation notifications to users who viewed this Hot Date
        viewers = HotDateView.objects.filter(hot_date=hot_date).exclude(user=request.user)
        for view in viewers:
            HotDateNotification.objects.create(
                user=view.user,
                hot_date=hot_date,
                notification_type='cancelled',
                message=f"Hot Date '{hot_date.title}' has been cancelled by the host"
            )
        
        return JsonResponse({
            'success': True, 
            'message': 'Hot Date cancelled successfully. Notifications sent to interested users.'
        })
        
    except HotDate.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Hot Date not found'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@login_required
def hotdate_notification_mark_read(request, notification_id):
    """Mark a Hot Date notification as read"""
    try:
        notification = HotDateNotification.objects.get(id=notification_id, user=request.user)
        notification.is_read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'success': True})
    except HotDateNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notification not found'})

# ADD THIS NEW VIEW FOR PROFILE CREATION
@login_required
def create_profile(request):
    """Handle comprehensive profile creation for new users"""
    # If user already has an approved profile, redirect to dashboard
    try:
        existing_profile = Profile.objects.get(user=request.user)
        if existing_profile.is_approved:
            return redirect('dashboard')
    except Profile.DoesNotExist:
        pass
    
    if request.method == 'POST':
        try:
            # Get or create profile
            profile, created = Profile.objects.get_or_create(user=request.user)
            
            # Update user's username
            username = request.POST.get('username', '').strip()
            if username and username != request.user.username:
                # Check if username is available
                if not User.objects.filter(username=username).exclude(id=request.user.id).exists():
                    request.user.username = username
                    request.user.save()
            
            # Update profile fields
            profile.headline = request.POST.get('headline', '')
            profile.about = request.POST.get('about', '')
            profile.location = request.POST.get('location', '')
            
            # Handle date of birth
            date_of_birth = request.POST.get('date_of_birth')
            if date_of_birth:
                profile.date_of_birth = date_of_birth
            
            profile.my_gender = request.POST.get('my_gender', '')
            profile.looking_for = request.POST.get('looking_for', '')
            
            # Handle array fields (convert to comma-separated strings)
            my_interests = request.POST.getlist('my_interests[]')
            profile.my_interests = ','.join(my_interests) if my_interests else ''
            
            must_have_tags = request.POST.getlist('must_have_tags[]')
            profile.must_have_tags = ','.join(must_have_tags) if must_have_tags else ''
            
            profile.children = request.POST.get('children', '')
            profile.smoking = request.POST.get('smoking', '')
            profile.drinking = request.POST.get('drinking', '')
            profile.exercise = request.POST.get('exercise', '')
            profile.pets = request.POST.get('pets', '')
            profile.diet = request.POST.get('diet', '')
            
            # Preferences
            profile.preferred_age_min = request.POST.get('preferred_age_min', 18)
            profile.preferred_age_max = request.POST.get('preferred_age_max', 99)
            profile.preferred_intent = request.POST.get('preferred_intent', '')
            profile.preferred_distance = request.POST.get('preferred_distance', '')
            
            # Mark as submitted for approval (but not approved yet)
            profile.is_approved = False
            profile.save()
            
            messages.success(request, 'Profile submitted for admin approval! You can now browse profiles in preview mode.')
            return redirect('preview_gate')
            
        except Exception as e:
            messages.error(request, f'Error creating profile: {str(e)}')
            print(f"DEBUG: Profile creation error: {e}")
    
    # GET request - show the form
    context = {
        'ages': range(18, 81),
    }
    return render(request, 'pages/create_your_profile.html', context)

# ADD THIS NEW VIEW FOR USERNAME CHECK
@login_required
def check_username(request):
    """Check if username is available"""
    username = request.GET.get('username', '').strip().lower()
    
    if not username or len(username) < 3:
        return JsonResponse({'available': False, 'error': 'Username too short'})
    
    # Check if username exists (excluding current user)
    exists = User.objects.filter(username__iexact=username).exclude(id=request.user.id).exists()
    
    return JsonResponse({'available': not exists})

@login_required
def preview_profile_detail(request, user_id):
    """Limited profile viewing for unapproved users"""
    # Redirect to full dashboard if user is approved
    try:
        user_profile = Profile.objects.get(user=request.user)
        if user_profile.is_approved or request.user.is_staff:
            return redirect('profile_detail', user_id=user_id)
    except Profile.DoesNotExist:
        pass
    
    # Get the target profile
    profile = get_object_or_404(Profile, user_id=user_id, is_approved=True)
    
    # Only show limited information
    context = {
        'profile': profile,
        'is_own_profile': False,
        'is_preview_mode': True,  # New flag for preview mode
    }
    return render(request, 'pages/preview_profile_detail.html', context)
